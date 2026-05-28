from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import AuditLog
from apps.members.views import admin_required


@admin_required
def audit_list(request):
    logs = AuditLog.objects.select_related('user').order_by('-timestamp')[:200]
    return render(request, 'audit/list.html', {'logs': logs})
