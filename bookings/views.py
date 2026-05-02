from rest_framework import serializers
from rest_framework import generics, status
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
from .conflict_engine import check_conflict, suggest_alternative_slots
from accounts.permissions import IsAdmin, IsApprover
from facilities.models import Facility


class BookingListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/bookings/  — List bookings (own for requesters, all for approvers/admins)
    POST /api/bookings/  — Submit a new booking request
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BookingCreateSerializer
        return BookingSerializer

    def get_queryset(self):
        user = self.request.user
        # Admins and approvers see all bookings
        if user.role in ['admin', 'approver']:
            return Booking.objects.all().select_related('user', 'facility')
        # Requesters only see their own
        return Booking.objects.filter(user=user).select_related('facility')

    def perform_create(self, serializer):
        facility = serializer.validated_data['facility']
        start_time = serializer.validated_data['start_time']
        end_time = serializer.validated_data['end_time']

        # Run conflict detection before saving
        conflicts = check_conflict(facility.id, start_time, end_time)

        if conflicts.exists():
            conflicting = conflicts.first()
            suggestions = suggest_alternative_slots(
                facility.id, start_time, end_time)

            # Log the conflict
            ConflictLog.objects.create(
                conflicting_booking=conflicting,
                facility=facility,
                requested_start=start_time,
                requested_end=end_time,
                resolution='Blocked — alternative slots suggested'
            )

            raise serializers.ValidationError({
                "conflict": {
                    "message": f"This slot conflicts with an existing booking by {conflicting.user.username}.",
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
    """
    GET    /api/bookings/<id>/  — View booking detail
    PATCH  /api/bookings/<id>/  — Update (admin only)
    DELETE /api/bookings/<id>/  — Cancel (own booking or admin)
    """
    queryset = Booking.objects.all().select_related('user', 'facility')
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
    """
    POST /api/bookings/check-conflict/
    Check if a time slot is available BEFORE submitting a booking.
    Returns conflict info and alternative slots if unavailable.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ConflictCheckSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        facility_id = serializer.validated_data['facility_id']
        start_time = serializer.validated_data['start_time']
        end_time = serializer.validated_data['end_time']

        facility = get_object_or_404(Facility, pk=facility_id)
        conflicts = check_conflict(facility_id, start_time, end_time)

        if conflicts.exists():
            conflicting = conflicts.first()
            suggestions = suggest_alternative_slots(
                facility_id, start_time, end_time)
            return Response({
                "available": False,
                "message":   f"Slot is not available — conflicts with an existing booking.",
                "conflicting_booking": {
                    "id":         conflicting.id,
                    "user":       conflicting.user.username,
                    "start_time": conflicting.start_time,
                    "end_time":   conflicting.end_time,
                    "status":     conflicting.status,
                },
                "alternative_slots": suggestions
            }, status=status.HTTP_200_OK)

        return Response({
            "available": True,
            "message":   f"'{facility.name}' is available for the requested slot.",
            "facility":  facility.name,
            "start_time": start_time,
            "end_time":   end_time,
        }, status=status.HTTP_200_OK)


# Fix missing import
