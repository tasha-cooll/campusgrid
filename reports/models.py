from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    ACTION_CHOICES = [
        # Booking actions
        ('booking_created',    'Booking Created'),
        ('booking_approved',   'Booking Approved'),
        ('booking_rejected',   'Booking Rejected'),
        ('booking_cancelled',  'Booking Cancelled'),
        ('booking_displaced',  'Booking Displaced'),
        ('conflict_detected',  'Conflict Detected'),
        ('priority_created',   'Priority Booking Created'),
        # User management actions
        ('user_registered',    'User Registered'),
        ('user_role_changed',  'User Role Changed'),
        ('user_activated',     'User Activated'),
        ('user_deactivated',   'User Deactivated'),
        # Facility actions
        ('facility_created',   'Facility Created'),
        ('facility_updated',   'Facility Updated'),
        ('facility_deleted',   'Facility Deleted'),
        # Admin actions
        ('admin_action',       'Admin Panel Action'),
    ]

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    details = models.TextField(blank=True, default='')
    booking = models.ForeignKey(
        'bookings.Booking',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='audit_logs'
    )
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='audit_logs_as_target'
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['actor']),
            models.Index(fields=['action']),
        ]

    def __str__(self):
        actor = self.actor.username if self.actor else 'System'
        return f'[{self.timestamp:%Y-%m-%d %H:%M}] {actor} — {self.get_action_display()}'
