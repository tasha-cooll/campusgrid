from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from bookings.models import Booking, BookingStatus
from .models import Notification, NotificationType


@receiver(post_save, sender=Booking)
def handle_booking_status_change(sender, instance, created, **kwargs):
    from reports.models import AuditLog

    if created:
        Notification.objects.create(
            user=instance.user,
            booking=instance,
            type=NotificationType.BOOKING_SUBMITTED,
            message=f"Your booking request for '{instance.facility.name}' on {instance.start_time:%B %d, %Y at %H:%M} has been submitted and is pending approval."
        )
        AuditLog.objects.create(
            actor=instance.user,
            booking=instance,
            action=AuditLog.Action.BOOKING_CREATED,
            details=f"Booking created for {instance.facility.name} on {instance.start_time:%Y-%m-%d %H:%M}"
        )
        if instance.is_priority:
            AuditLog.objects.create(
                actor=instance.user,
                booking=instance,
                action=AuditLog.Action.PRIORITY_CREATED,
                details=f"Priority booking created — {instance.priority_reason}"
            )
        _send_email(
            subject='CampusGrid - Booking Submitted',
            message=f"Your booking for {instance.facility.name} on {instance.start_time:%B %d, %Y} is pending approval.",
            recipient=instance.user.email
        )
    else:
        if instance.status == BookingStatus.APPROVED:
            Notification.objects.create(
                user=instance.user,
                booking=instance,
                type=NotificationType.BOOKING_APPROVED,
                message=f"Your booking for '{instance.facility.name}' on {instance.start_time:%B %d, %Y at %H:%M} has been approved."
            )
            AuditLog.objects.create(
                actor=instance.user,
                booking=instance,
                action=AuditLog.Action.BOOKING_APPROVED,
                details=f"Booking approved for {instance.facility.name} on {instance.start_time:%Y-%m-%d %H:%M}"
            )
            _send_email(
                subject='CampusGrid - Booking Approved',
                message=f"Your booking for {instance.facility.name} on {instance.start_time:%B %d, %Y} has been approved.",
                recipient=instance.user.email
            )
        elif instance.status == BookingStatus.REJECTED:
            Notification.objects.create(
                user=instance.user,
                booking=instance,
                type=NotificationType.BOOKING_REJECTED,
                message=f"Your booking request for '{instance.facility.name}' on {instance.start_time:%B %d, %Y at %H:%M} was not approved."
            )
            AuditLog.objects.create(
                actor=instance.user,
                booking=instance,
                action=AuditLog.Action.BOOKING_REJECTED,
                details=f"Booking rejected for {instance.facility.name} on {instance.start_time:%Y-%m-%d %H:%M}"
            )
            _send_email(
                subject='CampusGrid - Booking Rejected',
                message=f"Your booking for {instance.facility.name} on {instance.start_time:%B %d, %Y} was not approved.",
                recipient=instance.user.email
            )
        elif instance.status == BookingStatus.CANCELLED:
            Notification.objects.create(
                user=instance.user,
                booking=instance,
                type=NotificationType.BOOKING_CANCELLED,
                message=f"Your booking for '{instance.facility.name}' on {instance.start_time:%B %d, %Y at %H:%M} has been cancelled."
            )
            AuditLog.objects.create(
                actor=instance.user,
                booking=instance,
                action=AuditLog.Action.BOOKING_CANCELLED,
                details=f"Booking cancelled for {instance.facility.name} on {instance.start_time:%Y-%m-%d %H:%M}"
            )
        elif instance.status == BookingStatus.DISPLACED:
            Notification.objects.create(
                user=instance.user,
                booking=instance,
                type=NotificationType.BOOKING_DISPLACED,
                message=f"Your booking for '{instance.facility.name}' on {instance.start_time:%B %d, %Y at %H:%M} has been displaced by a university priority event. Please submit a new request for an alternative slot."
            )
            AuditLog.objects.create(
                actor=instance.user,
                booking=instance,
                action=AuditLog.Action.BOOKING_DISPLACED,
                details=f"Booking displaced by priority event for {instance.facility.name} on {instance.start_time:%Y-%m-%d %H:%M}"
            )
            _send_email(
                subject='CampusGrid - Booking Displaced',
                message=f"Your booking for {instance.facility.name} on {instance.start_time:%B %d, %Y} has been displaced by a university priority event.",
                recipient=instance.user.email
            )


def _send_email(subject, message, recipient):
    if not recipient:
        return
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=True,
        )
    except Exception:
        pass
