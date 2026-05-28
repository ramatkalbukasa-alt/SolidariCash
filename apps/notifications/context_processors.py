def notifications_processor(request):
    if request.user.is_authenticated:
        unread_count = request.user.notifications.filter(is_read=False).count()
        recent = request.user.notifications.filter(is_read=False).order_by('-created_at')[:5]
        pending_emergencies_count = 0
        if request.user.is_admin:
            try:
                from apps.emergencies.models import Emergency
                pending_emergencies_count = Emergency.objects.filter(status=Emergency.STATUS_PENDING).count()
            except Exception:
                pass
        return {
            'unread_notifications_count': unread_count,
            'recent_notifications': recent,
            'pending_emergencies_count': pending_emergencies_count,
        }
    return {'unread_notifications_count': 0, 'recent_notifications': [], 'pending_emergencies_count': 0}
