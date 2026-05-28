from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import Notification


@login_required
def notification_list(request):
    notifications = request.user.notifications.order_by('-created_at')[:50]
    return render(request, 'notifications/list.html', {'notifications': notifications})


@login_required
def mark_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.is_read = True
    notif.read_at = timezone.now()
    notif.save(update_fields=['is_read', 'read_at'])
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok'})
    return notification_list(request)


@login_required
def mark_all_read(request):
    if request.method == 'POST':
        request.user.notifications.filter(is_read=False).update(
            is_read=True, read_at=timezone.now()
        )
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok'})
    return notification_list(request)
