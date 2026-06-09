def log_action(actor, action, details='', booking=None, target_user=None, request=None):
    """
    Central utility to create audit log entries from anywhere in the codebase.
    Import this function and call it after any significant action.
    """
    from reports.models import AuditLog

    ip = None
    if request:
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded.split(
            ',')[0] if x_forwarded else request.META.get('REMOTE_ADDR')

    AuditLog.objects.create(
        actor=actor,
        action=action,
        details=details,
        booking=booking,
        target_user=target_user,
        ip_address=ip,
    )
