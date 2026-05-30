from .models import AuditLog


def log_action(request, action, model_name, object_id='', object_repr='', changes=None, extra_data=None):
    """Journaliser une action dans l'audit log."""
    try:
        user = request.user if request and request.user.is_authenticated else None
        ip = _get_client_ip(request) if request else None
        ua = request.META.get('HTTP_USER_AGENT', '')[:500] if request else ''

        AuditLog.objects.create(
            user=user,
            action=action,
            model_name=model_name,
            object_id=str(object_id),
            object_repr=str(object_repr)[:200],
            changes=changes or {},
            ip_address=ip,
            user_agent=ua,
            extra_data=extra_data or {},
        )
    except Exception:
        pass


def _get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')
