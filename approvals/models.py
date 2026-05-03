from django.db import models
from django.conf import settings
from bookings.models import Booking


class Approval(models.Model):
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name='approval'
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='approvals_made'
    )
    decision = models.CharField(
        max_length=20,
        choices=[('approved', 'Approved'), ('rejected', 'Rejected')]
    )
    comments = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-reviewed_at']

    def __str__(self):
        return f"{self.decision.upper()} — {self.booking} by {self.reviewed_by}"
