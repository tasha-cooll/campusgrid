from django.db import models
from django.conf import settings
from facilities.models import Facility, FacilityZone


class BookingStatus(models.TextChoices):
    PENDING = 'pending',    'Pending'
    APPROVED = 'approved',   'Approved'
    REJECTED = 'rejected',   'Rejected'
    CANCELLED = 'cancelled',  'Cancelled'
    DISPLACED = 'displaced',  'Displaced by Priority Event'


class Booking(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    facility = models.ForeignKey(
        Facility,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    zone = models.ForeignKey(
        FacilityZone,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='bookings',
        help_text="Specific zone within the facility. Leave blank to book entire facility."
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    purpose = models.CharField(max_length=255)
    expected_attendance = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING
    )
    notes = models.TextField(blank=True)

    # Priority booking fields
    is_priority = models.BooleanField(
        default=False,
        help_text="Priority bookings displace existing bookings. Admin only."
    )
    priority_reason = models.CharField(
        max_length=255,
        blank=True,
        help_text="Reason for priority e.g. Graduation Ceremony, UEAB Board Meeting"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        zone_str = f" [{self.zone.name}]" if self.zone else ""
        priority_str = " ⚡PRIORITY" if self.is_priority else ""
        return f"{self.user.username} — {self.facility.name}{zone_str}{priority_str} [{self.start_time:%Y-%m-%d %H:%M}]"


class ConflictLog(models.Model):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='conflicts',
        null=True, blank=True
    )
    conflicting_booking = models.ForeignKey(
        Booking,
        on_delete=models.SET_NULL,
        related_name='conflicted_by',
        null=True, blank=True
    )
    facility = models.ForeignKey(
        Facility,
        on_delete=models.CASCADE,
        related_name='conflict_logs'
    )
    zone = models.ForeignKey(
        FacilityZone,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='conflict_logs'
    )
    requested_start = models.DateTimeField()
    requested_end = models.DateTimeField()
    detected_at = models.DateTimeField(auto_now_add=True)
    resolution = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-detected_at']

    def __str__(self):
        return f"Conflict on {self.facility.name} at {self.requested_start:%Y-%m-%d %H:%M}"
