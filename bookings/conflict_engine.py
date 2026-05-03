from datetime import timedelta
from django.utils import timezone
from .models import Booking, BookingStatus


def check_recurring_block(facility_id, start_time, end_time, zone_id=None):
    """
    Check if the requested slot falls within any active recurring block
    for the facility or zone.
    Returns the blocking RecurringBlock if found, None otherwise.
    """
    from facilities.models import RecurringBlock

    day_of_week = start_time.weekday()
    request_start = start_time.time()
    request_end = end_time.time()

    blocks = RecurringBlock.objects.filter(
        facility_id=facility_id,
        day_of_week=day_of_week,
        is_active=True,
        start_time__lt=request_end,
        end_time__gt=request_start,
    )

    if zone_id:
        blocks = blocks.filter(
            models.Q(zone_id=zone_id) | models.Q(zone__isnull=True)
        )

    return blocks.first()


def check_conflict(facility_id, start_time, end_time, zone_id=None, exclude_booking_id=None):
    """
    Check if a requested time slot conflicts with any existing
    approved or pending bookings.

    Zone-aware: if zone_id provided, only conflicts within that zone
    or whole-facility bookings are flagged.
    """
    queryset = Booking.objects.filter(
        facility_id=facility_id,
        status__in=[BookingStatus.PENDING, BookingStatus.APPROVED],
        start_time__lt=end_time,
        end_time__gt=start_time,
    )

    if zone_id:
        from django.db.models import Q
        queryset = queryset.filter(
            Q(zone_id=zone_id) | Q(zone__isnull=True)
        )

    if exclude_booking_id:
        queryset = queryset.exclude(id=exclude_booking_id)

    return queryset


def get_displaced_bookings(facility_id, start_time, end_time, zone_id=None):
    """
    Get all bookings that would be displaced by a priority booking.
    Returns pending and approved bookings in the conflicting slot.
    """
    return check_conflict(facility_id, start_time, end_time, zone_id)


def suggest_alternative_slots(facility_id, start_time, end_time, zone_id=None, count=3):
    """
    Suggest nearest available alternative slots of the same duration.
    Respects both existing bookings and recurring blocks.
    """
    duration = end_time - start_time
    suggestions = []
    current = end_time
    max_search = start_time + timedelta(days=7)
    step = timedelta(minutes=30)

    while len(suggestions) < count and current < max_search:
        candidate_start = current
        candidate_end = current + duration

        # Check existing booking conflicts
        booking_conflict = check_conflict(
            facility_id, candidate_start, candidate_end, zone_id
        )

        # Check recurring block conflicts
        recurring_conflict = check_recurring_block(
            facility_id, candidate_start, candidate_end, zone_id
        )

        if not booking_conflict.exists() and not recurring_conflict:
            suggestions.append({
                'start_time':       candidate_start.isoformat(),
                'end_time':         candidate_end.isoformat(),
                'duration_minutes': int(duration.total_seconds() / 60),
            })

        current += step

    return suggestions
