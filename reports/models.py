from django.db import models
from django.conf import settings
from bookings.models import Booking


class AuditLog(models.Model):
    """
    Immutable record of every significant action in the system.
    Written automatically by signals — never manually.
    """

    class Action(models.TextChoices):
        BOOKING_CREATED = 'booking_created',   'Booking Created'
        BOOKING_APPROVED = 'booking_approved',  'Booking Approved'
        BOOKING_REJECTED = 'booking_rejected',  'Booking Rejected'
        BOOKING_CANCELLED = 'booking_cancelled', 'Booking Cancelled'
        BOOKING_DISPLACED = 'booking_displaced', 'Booking Displaced'
        CONFLICT_DETECTED = 'conflict_detected', 'Conflict Detected'
        PRIORITY_CREATED = 'priority_created',  'Priority Booking Created'

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    booking = models.ForeignKey(
        Booking,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=50, choices=Action.choices)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Audit Log Entry'
        verbose_name_plural = 'Audit Log'

    def __str__(self):
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {self.action} — {self.actor}"
