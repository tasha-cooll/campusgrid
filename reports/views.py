from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from django.utils import timezone
from django.db.models import Count, Q
from datetime import datetime, timedelta
import pytz

from .models import AuditLog
from .serializers import AuditLogSerializer
from bookings.models import Booking, BookingStatus, ConflictLog
from facilities.models import Facility
from accounts.permissions import IsAdmin, IsApprover


class CalendarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        facility_id = request.query_params.get('facility_id')
        month = int(request.query_params.get('month', timezone.now().month))
        year = int(request.query_params.get('year', timezone.now().year))

        nairobi = pytz.timezone('Africa/Nairobi')
        start_of_month = nairobi.localize(datetime(year, month, 1, 0, 0, 0))
        if month == 12:
            end_of_month = nairobi.localize(datetime(year + 1, 1, 1, 0, 0, 0))
        else:
            end_of_month = nairobi.localize(
                datetime(year, month + 1, 1, 0, 0, 0))

        bookings = Booking.objects.filter(
            status__in=[BookingStatus.APPROVED, BookingStatus.PENDING,
                        BookingStatus.DISPLACED],
            start_time__gte=start_of_month,
            start_time__lt=end_of_month,
        ).select_related('user', 'facility', 'zone')

        if facility_id:
            bookings = bookings.filter(facility_id=facility_id)

        calendar_data = []
        for booking in bookings:
            calendar_data.append({
                'id':          booking.id,
                'title':       f"{booking.purpose} — {booking.user.username}",
                'facility':    booking.facility.name,
                'zone':        booking.zone.name if booking.zone else 'Entire Facility',
                'start':       booking.start_time.isoformat(),
                'end':         booking.end_time.isoformat(),
                'status':      booking.status,
                'is_priority': booking.is_priority,
                'color':       _get_status_color(booking.status, booking.is_priority),
            })

        return Response({
            'month':    month,
            'year':     year,
            'facility': facility_id,
            'count':    len(calendar_data),
            'events':   calendar_data,
        })


class UtilizationReportView(APIView):
    permission_classes = [IsApprover]

    def get(self, request):
        month = int(request.query_params.get('month', timezone.now().month))
        year = int(request.query_params.get('year',  timezone.now().year))

        nairobi = pytz.timezone('Africa/Nairobi')
        start_of_month = nairobi.localize(datetime(year, month, 1, 0, 0, 0))
        if month == 12:
            end_of_month = nairobi.localize(datetime(year + 1, 1, 1, 0, 0, 0))
        else:
            end_of_month = nairobi.localize(
                datetime(year, month + 1, 1, 0, 0, 0))

        facilities = Facility.objects.filter(is_active=True)
        report = []

        for facility in facilities:
            bookings = Booking.objects.filter(
                facility=facility,
                start_time__gte=start_of_month,
                start_time__lt=end_of_month,
            )

            total = bookings.count()
            approved = bookings.filter(status=BookingStatus.APPROVED).count()
            rejected = bookings.filter(status=BookingStatus.REJECTED).count()
            pending = bookings.filter(status=BookingStatus.PENDING).count()
            cancelled = bookings.filter(status=BookingStatus.CANCELLED).count()
            displaced = bookings.filter(status=BookingStatus.DISPLACED).count()
            conflicts = ConflictLog.objects.filter(
                facility=facility,
                detected_at__gte=start_of_month,
                detected_at__lt=end_of_month,
            ).count()

            approved_bookings = bookings.filter(status=BookingStatus.APPROVED)
            total_hours = sum(
                (b.end_time - b.start_time).total_seconds() / 3600
                for b in approved_bookings
            )

            report.append({
                'facility':           facility.name,
                'facility_id':        facility.id,
                'total_bookings':     total,
                'approved':           approved,
                'rejected':           rejected,
                'pending':            pending,
                'cancelled':          cancelled,
                'displaced':          displaced,
                'conflicts':          conflicts,
                'total_hours_booked': round(total_hours, 1),
            })

        return Response({
            'month':      month,
            'year':       year,
            'facilities': report,
        })


class ConflictReportView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        month = int(request.query_params.get('month', timezone.now().month))
        year = int(request.query_params.get('year',  timezone.now().year))

        nairobi = pytz.timezone('Africa/Nairobi')
        start_of_month = nairobi.localize(datetime(year, month, 1, 0, 0, 0))
        if month == 12:
            end_of_month = nairobi.localize(datetime(year + 1, 1, 1, 0, 0, 0))
        else:
            end_of_month = nairobi.localize(
                datetime(year, month + 1, 1, 0, 0, 0))

        conflicts = ConflictLog.objects.filter(
            detected_at__gte=start_of_month,
            detected_at__lt=end_of_month,
        ).select_related('facility', 'zone')

        by_facility = {}
        for conflict in conflicts:
            name = conflict.facility.name
            if name not in by_facility:
                by_facility[name] = 0
            by_facility[name] += 1

        return Response({
            'month':           month,
            'year':            year,
            'total_conflicts': conflicts.count(),
            'by_facility':     by_facility,
            'conflict_log': [
                {
                    'facility':        c.facility.name,
                    'zone':            c.zone.name if c.zone else 'Entire Facility',
                    'requested_start': c.requested_start,
                    'requested_end':   c.requested_end,
                    'detected_at':     c.detected_at,
                    'resolution':      c.resolution,
                }
                for c in conflicts
            ]
        })


class DashboardSummaryView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        now = timezone.now()
        nairobi = pytz.timezone('Africa/Nairobi')
        start_of_month = nairobi.localize(
            datetime(now.year, now.month, 1, 0, 0, 0))
        if now.month == 12:
            end_of_month = nairobi.localize(
                datetime(now.year + 1, 1, 1, 0, 0, 0))
        else:
            end_of_month = nairobi.localize(
                datetime(now.year, now.month + 1, 1, 0, 0, 0))

        this_month = Booking.objects.filter(
            created_at__gte=start_of_month,
            created_at__lt=end_of_month,
        )

        return Response({
            'total_bookings_this_month': this_month.count(),
            'pending_approvals':         Booking.objects.filter(status=BookingStatus.PENDING).count(),
            'approved_this_month':       this_month.filter(status=BookingStatus.APPROVED).count(),
            'rejected_this_month':       this_month.filter(status=BookingStatus.REJECTED).count(),
            'conflicts_this_month':      ConflictLog.objects.filter(
                detected_at__gte=start_of_month,
                detected_at__lt=end_of_month,
            ).count(),
            'total_facilities':          Facility.objects.filter(is_active=True).count(),
            'total_users':               Booking.objects.values('user').distinct().count(),
            'recent_audit_logs':         AuditLogSerializer(
                AuditLog.objects.all()[:5],
                many=True
            ).data,
        })


class AuditLogView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        queryset = AuditLog.objects.all().select_related('actor', 'booking__facility')
        action = self.request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)
        return queryset


def _get_status_color(status, is_priority):
    if is_priority:
        return '#8B0000'
    colors = {
        'approved':  '#2E75B6',
        'pending':   '#F4A261',
        'rejected':  '#E63946',
        'cancelled': '#999999',
        'displaced': '#FF6B35',
    }
    return colors.get(status, '#2E75B6')
