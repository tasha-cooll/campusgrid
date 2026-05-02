from datetime import timedelta
from django.utils import timezone
from .models import Booking, BookingStatus


def check_conflict(facility_id, start_time, end_time, exclude_booking_id=None):
    """
    Check if a requested time slot conflicts with any existing approved
    or pending bookings for the given facility.

    Returns a queryset of conflicting bookings (empty if no conflict).
    """
    queryset = Booking.objects.filter(
        facility_id=facility_id,
        status__in=[BookingStatus.PENDING, BookingStatus.APPROVED],
        start_time__lt=end_time,
        end_time__gt=start_time,
    )

    if exclude_booking_id:
        queryset = queryset.exclude(id=exclude_booking_id)

    return queryset


def suggest_alternative_slots(facility_id, start_time, end_time, count=3):
    """
    When a conflict is detected, suggest <count> nearest available
    time slots of the same duration on the same facility.

    Strategy:
    - Try the same duration slot starting right after the conflict ends
    - Step forward in 30-minute increments until <count> free slots found
    - Search up to 7 days ahead
    """
    duration = end_time - start_time
    suggestions = []
    current = end_time  # Start searching from the end of the requested slot
    max_search = start_time + timedelta(days=7)
    step = timedelta(minutes=30)

    while len(suggestions) < count and current < max_search:
        candidate_start = current
        candidate_end = current + duration

        conflicts = check_conflict(facility_id, candidate_start, candidate_end)

        if not conflicts.exists():
            suggestions.append({
                'start_time': candidate_start.isoformat(),
                'end_time':   candidate_end.isoformat(),
                'duration_minutes': int(duration.total_seconds() / 60),
            })

        current += step

    return suggestions
