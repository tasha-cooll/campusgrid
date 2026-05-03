from datetime import timedelta
from django.utils import timezone
from .models import Booking, BookingStatus


def check_recurring_block(facility_id, start_time, end_time, zone_id=None):
    from facilities.models import RecurringBlock
    from django.db.models import Q

    local_start = timezone.localtime(start_time)
    local_end = timezone.localtime(end_time)
    day_of_week = local_start.weekday()

    request_start = local_start.time()
    request_end = local_end.time()

    blocks = RecurringBlock.objects.filter(
        facility_id=facility_id,
        day_of_week=day_of_week,
        is_active=True,
        start_time__lt=request_end,
        end_time__gt=request_start,
    )

    if zone_id:
        blocks = blocks.filter(
            Q(zone_id=zone_id) | Q(zone__isnull=True)
        )

    return blocks.first()


def check_conflict(facility_id, start_time, end_time, zone_id=None, exclude_booking_id=None):
    from django.db.models import Q

    queryset = Booking.objects.filter(
        facility_id=facility_id,
        status__in=[BookingStatus.PENDING, BookingStatus.APPROVED],
        start_time__lt=end_time,
        end_time__gt=start_time,
    )

    if zone_id:
        queryset = queryset.filter(
            Q(zone_id=zone_id) | Q(zone__isnull=True)
        )

    if exclude_booking_id:
        queryset = queryset.exclude(id=exclude_booking_id)

    return queryset


def get_displaced_bookings(facility_id, start_time, end_time, zone_id=None):
    return check_conflict(facility_id, start_time, end_time, zone_id)


def suggest_alternative_slots(facility_id, start_time, end_time, zone_id=None, count=3):
    duration = end_time - start_time
    suggestions = []
    current = end_time
    max_search = start_time + timedelta(days=7)
    step = timedelta(minutes=30)

    while len(suggestions) < count and current < max_search:
        candidate_start = current
        candidate_end = current + duration

        booking_conflict = check_conflict(
            facility_id, candidate_start, candidate_end, zone_id)
        recurring_conflict = check_recurring_block(
            facility_id, candidate_start, candidate_end, zone_id)

        if not booking_conflict.exists() and not recurring_conflict:
            suggestions.append({
                'start_time':       candidate_start.isoformat(),
                'end_time':         candidate_end.isoformat(),
                'duration_minutes': int(duration.total_seconds() / 60),
            })

        current += step

    return suggestions
