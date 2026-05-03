from rest_framework import generics, status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Booking, BookingStatus, ConflictLog
from .serializers import (
    BookingSerializer,
    BookingCreateSerializer,
    ConflictCheckSerializer,
)
from .conflict_engine import (
    check_conflict,
    check_recurring_block,
    suggest_alternative_slots,
    get_displaced_bookings,
)
from accounts.permissions import IsAdmin, IsApprover
from facilities.models import Facility


class BookingListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BookingCreateSerializer
        return BookingSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'approver']:
            return Booking.objects.all().select_related('user', 'facility', 'zone')
        return Booking.objects.filter(user=user).select_related('facility', 'zone')

    def perform_create(self, serializer):
        facility = serializer.validated_data['facility']
        zone = serializer.validated_data.get('zone', None)
        start_time = serializer.validated_data['start_time']
        end_time = serializer.validated_data['end_time']
        is_priority = serializer.validated_data.get('is_priority', False)
        zone_id = zone.id if zone else None

        # Only admins can create priority bookings
        if is_priority and self.request.user.role != 'admin':
            raise serializers.ValidationError({
                "error": "Only administrators can create priority bookings."
            })

        # Check recurring blocks first — priority bookings bypass this
        if not is_priority:
            recurring_block = check_recurring_block(
                facility.id, start_time, end_time, zone_id
            )
            if recurring_block:
                raise serializers.ValidationError({
                    "recurring_block": {
                        "message": f"This slot is permanently blocked — {recurring_block.label}.",
                        "blocked_by": recurring_block.label,
                        "day":        recurring_block.get_day_of_week_display(),
                        "time":       f"{recurring_block.start_time} – {recurring_block.end_time}",
                        "note":       "This is a recurring event. Please choose a different time."
                    }
                })

        # Check booking conflicts
        conflicts = check_conflict(facility.id, start_time, end_time, zone_id)

        if conflicts.exists():
            if is_priority:
                # Priority booking — displace all conflicting bookings
                displaced_users = []
                for conflicting in conflicts:
                    conflicting.status = BookingStatus.DISPLACED
                    conflicting.save()
                    displaced_users.append(conflicting.user.username)

                # Save the priority booking
                booking = serializer.save(user=self.request.user)

                # Log the displacement
                ConflictLog.objects.create(
                    booking=booking,
                    facility=facility,
                    zone=zone,
                    requested_start=start_time,
                    requested_end=end_time,
                    resolution=f"Priority booking — displaced {len(displaced_users)} booking(s)"
                )
                return

            else:
                # Regular booking — block and suggest alternatives
                conflicting = conflicts.first()
                suggestions = suggest_alternative_slots(
                    facility.id, start_time, end_time, zone_id
                )

                ConflictLog.objects.create(
                    conflicting_booking=conflicting,
                    facility=facility,
                    zone=zone,
                    requested_start=start_time,
                    requested_end=end_time,
                    resolution='Blocked — alternative slots suggested'
                )

                raise serializers.ValidationError({
                    "conflict": {
                        "message":   f"This slot conflicts with an existing booking.",
                        "conflicting_booking": {
                            "id":         conflicting.id,
                            "start_time": conflicting.start_time,
                            "end_time":   conflicting.end_time,
                            "status":     conflicting.status,
                        },
                        "alternative_slots": suggestions
                    }
                })

        serializer.save(user=self.request.user)


class BookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Booking.objects.all().select_related('user', 'facility', 'zone')
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        booking = self.get_object()
        if booking.user != request.user and request.user.role != 'admin':
            return Response(
                {"error": "You can only cancel your own bookings."},
                status=status.HTTP_403_FORBIDDEN
            )
        booking.status = BookingStatus.CANCELLED
        booking.save()
        return Response(
            {"message": "Booking cancelled successfully."},
            status=status.HTTP_200_OK
        )


class ConflictCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ConflictCheckSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        facility_id = serializer.validated_data['facility_id']
        start_time = serializer.validated_data['start_time']
        end_time = serializer.validated_data['end_time']
        zone_id = serializer.validated_data.get('zone_id', None)

        facility = get_object_or_404(Facility, pk=facility_id)

        # Check recurring blocks
        recurring_block = check_recurring_block(
            facility_id, start_time, end_time, zone_id)
        if recurring_block:
            return Response({
                "available":   False,
                "reason":      "recurring_block",
                "message":     f"This slot is permanently blocked — {recurring_block.label}.",
                "blocked_by":  recurring_block.label,
                "time":        f"{recurring_block.start_time} – {recurring_block.end_time}",
            }, status=status.HTTP_200_OK)

        # Check booking conflicts
        conflicts = check_conflict(facility_id, start_time, end_time, zone_id)
        if conflicts.exists():
            conflicting = conflicts.first()
            suggestions = suggest_alternative_slots(
                facility_id, start_time, end_time, zone_id)
            return Response({
                "available":   False,
                "reason":      "booking_conflict",
                "message":     "Slot is not available.",
                "conflicting_booking": {
                    "id":         conflicting.id,
                    "user":       conflicting.user.username,
                    "start_time": conflicting.start_time,
                    "end_time":   conflicting.end_time,
                },
                "alternative_slots": suggestions
            }, status=status.HTTP_200_OK)

        return Response({
            "available":  True,
            "message":    f"'{facility.name}' is available for the requested slot.",
            "start_time": start_time,
            "end_time":   end_time,
        }, status=status.HTTP_200_OK)
