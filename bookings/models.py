from django.db import models
from django.conf import settings
from facilities.models import Facility


class BookingStatus(models.TextChoices):
    PENDING = 'pending',  'Pending'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'
    CANCELLED = 'cancelled', 'Cancelled'


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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} — {self.facility.name} [{self.start_time:%Y-%m-%d %H:%M}]"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                raise ValidationError("End time must be after start time.")


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
    requested_start = models.DateTimeField()
    requested_end = models.DateTimeField()
    detected_at = models.DateTimeField(auto_now_add=True)
    resolution = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-detected_at']

    def __str__(self):
        return f"Conflict on {self.facility.name} at {self.requested_start:%Y-%m-%d %H:%M}"
