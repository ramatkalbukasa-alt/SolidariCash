from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'recipient', 'notification_type', 'category', 'is_read', 'created_at']
    list_filter = ['notification_type', 'category', 'is_read']
    search_fields = ['recipient__username', 'title']
    readonly_fields = ['created_at', 'read_at']
