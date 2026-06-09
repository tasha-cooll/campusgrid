from django.contrib.admin.models import LogEntry
from django.db.models.signals import post_save
from django.dispatch import receiver
from bookings.models import Booking, BookingStatus
from .models import Notification
from reports.models import AuditLog


def _send_email(user, subject, message):
    from django.core.mail import send_mail
    from django.conf import settings
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                  [user.email], fail_silently=True)
    except Exception:
        pass


@receiver(post_save, sender=Booking)
def handle_booking_status_change(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.user,
            booking=instance,
            type='booking_submitted',
            message=f'Your booking for {instance.facility.name} on {instance.start_time:%d %b %Y} has been submitted and is awaiting approval.',
        )
        _send_email(
            instance.user,
            'CampusGrid — Booking Submitted',
            f'Your booking for {instance.facility.name} on {instance.start_time:%d %b %Y} has been submitted.',
        )
        AuditLog.objects.create(
            actor=instance.user,
            action='booking_created',
            details=f'Booking created for {instance.facility.name} on {instance.start_time:%d %b %Y %H:%M}',
            booking=instance,
        )

    elif instance.status == BookingStatus.APPROVED:
        Notification.objects.create(
            user=instance.user,
            booking=instance,
            type='booking_approved',
            message=f'Your booking for {instance.facility.name} on {instance.start_time:%d %b %Y} has been approved.',
        )
        _send_email(
            instance.user,
            'CampusGrid — Booking Approved',
            f'Your booking for {instance.facility.name} on {instance.start_time:%d %b %Y} has been approved.',
        )
        AuditLog.objects.create(
            actor=instance.user,
            action='booking_approved',
            details=f'Booking approved for {instance.facility.name} on {instance.start_time:%d %b %Y %H:%M}',
            booking=instance,
        )

    elif instance.status == BookingStatus.REJECTED:
        Notification.objects.create(
            user=instance.user,
            booking=instance,
            type='booking_rejected',
            message=f'Your booking for {instance.facility.name} on {instance.start_time:%d %b %Y} has been rejected.',
        )
        AuditLog.objects.create(
            actor=instance.user,
            action='booking_rejected',
            details=f'Booking rejected for {instance.facility.name} on {instance.start_time:%d %b %Y %H:%M}',
            booking=instance,
        )

    elif instance.status == BookingStatus.CANCELLED:
        Notification.objects.create(
            user=instance.user,
            booking=instance,
            type='booking_cancelled',
            message=f'Your booking for {instance.facility.name} on {instance.start_time:%d %b %Y} has been cancelled.',
        )
        AuditLog.objects.create(
            actor=instance.user,
            action='booking_cancelled',
            details=f'Booking cancelled for {instance.facility.name} on {instance.start_time:%d %b %Y %H:%M}',
            booking=instance,
        )

    elif instance.status == BookingStatus.DISPLACED:
        Notification.objects.create(
            user=instance.user,
            booking=instance,
            type='booking_displaced',
            message=f'Your booking for {instance.facility.name} on {instance.start_time:%d %b %Y} has been displaced by a priority booking.',
        )
        AuditLog.objects.create(
            actor=instance.user,
            action='booking_displaced',
            details=f'Booking displaced for {instance.facility.name} on {instance.start_time:%d %b %Y %H:%M}',
            booking=instance,
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


@receiver(post_save, sender=LogEntry)
def handle_admin_log_entry(sender, instance, created, **kwargs):
    if not created:
        return
    try:
        action_map = {1: 'admin_action', 2: 'admin_action', 3: 'admin_action'}
        AuditLog.objects.create(
            actor=instance.user,
            action='admin_action',
            details='Admin panel: {} — {} "{}"'.format(
                instance.get_action_flag_display(),
                instance.content_type.model.title() if instance.content_type else 'Object',
                instance.object_repr,
            ),
        )
    except Exception:
        pass
