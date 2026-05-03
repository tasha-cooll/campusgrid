from django.db import models
from django.conf import settings
from bookings.models import Booking


class NotificationType(models.TextChoices):
    BOOKING_SUBMITTED = 'booking_submitted', 'Booking Submitted'
    BOOKING_APPROVED = 'booking_approved',  'Booking Approved'
    BOOKING_REJECTED = 'booking_rejected',  'Booking Rejected'
    BOOKING_CANCELLED = 'booking_cancelled', 'Booking Cancelled'
    BOOKING_DISPLACED = 'booking_displaced', 'Booking Displaced by Priority Event'
    CONFLICT_DETECTED = 'conflict_detected', 'Conflict Detected'


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True, blank=True
    )
    type = models.CharField(max_length=50, choices=NotificationType.choices)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.user.username} — {self.type} ({'read' if self.is_read else 'unread'})"
