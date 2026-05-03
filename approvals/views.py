from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Approval
from .serializers import ApprovalSerializer, ApprovalActionSerializer
from bookings.models import Booking, BookingStatus
from accounts.permissions import IsApprover, IsAdmin


class PendingBookingsView(generics.ListAPIView):
    """
    GET /api/approvals/pending/
    Returns all bookings with status PENDING.
    Approvers and Admins only.
    """
    serializer_class = ApprovalSerializer
    permission_classes = [IsApprover]

    def get_queryset(self):
        # Return pending bookings wrapped as approvals
        pending = Booking.objects.filter(
            status=BookingStatus.PENDING
        ).select_related('user', 'facility')
        return Approval.objects.filter(
            booking__status=BookingStatus.PENDING
        ).select_related('booking__user', 'booking__facility')

    def list(self, request, *args, **kwargs):
        pending_bookings = Booking.objects.filter(
            status=BookingStatus.PENDING
        ).select_related('user', 'facility')

        from bookings.serializers import BookingSerializer
        serializer = BookingSerializer(pending_bookings, many=True)
        return Response({
            "count":    pending_bookings.count(),
            "bookings": serializer.data
        })


class ApproveBookingView(APIView):
    """
    POST /api/approvals/<booking_id>/approve/
    Approver or Admin approves a pending booking.
    """
    permission_classes = [IsApprover]

    def post(self, request, booking_id):
        try:
            booking = Booking.objects.get(
                id=booking_id, status=BookingStatus.PENDING)
        except Booking.DoesNotExist:
            return Response(
                {"error": "Pending booking not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ApprovalActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Update booking status
        booking.status = BookingStatus.APPROVED
        booking.save()

        # Create approval record
        approval = Approval.objects.create(
            booking=booking,
            reviewed_by=request.user,
            decision='approved',
            comments=serializer.validated_data.get('comments', '')
        )

        return Response({
            "message":  f"Booking approved successfully.",
            "booking":  str(booking),
            "approval": ApprovalSerializer(approval).data
        }, status=status.HTTP_200_OK)


class RejectBookingView(APIView):
    """
    POST /api/approvals/<booking_id>/reject/
    Approver or Admin rejects a pending booking.
    """
    permission_classes = [IsApprover]

    def post(self, request, booking_id):
        try:
            booking = Booking.objects.get(
                id=booking_id, status=BookingStatus.PENDING)
        except Booking.DoesNotExist:
            return Response(
                {"error": "Pending booking not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ApprovalActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Update booking status
        booking.status = BookingStatus.REJECTED
        booking.save()

        # Create approval record
        approval = Approval.objects.create(
            booking=booking,
            reviewed_by=request.user,
            decision='rejected',
            comments=serializer.validated_data.get('comments', '')
        )

        return Response({
            "message":  f"Booking rejected.",
            "booking":  str(booking),
            "approval": ApprovalSerializer(approval).data
        }, status=status.HTTP_200_OK)


class ApprovalHistoryView(generics.ListAPIView):
    """
    GET /api/approvals/history/
    Full approval history. Admins only.
    """
    queryset = Approval.objects.all().select_related(
        'booking__user', 'booking__facility', 'reviewed_by'
    )
    serializer_class = ApprovalSerializer
    permission_classes = [IsAdmin]
