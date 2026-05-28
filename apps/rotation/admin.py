from django.contrib import admin
from .models import RotationOrder, RotationHistory


@admin.register(RotationOrder)
class RotationOrderAdmin(admin.ModelAdmin):
    list_display = ['position', 'head', 'cycle', 'status', 'is_emergency']
    list_filter = ['status', 'cycle', 'is_emergency']
    ordering = ['cycle', 'position']


@admin.register(RotationHistory)
class RotationHistoryAdmin(admin.ModelAdmin):
    list_display = ['rotation_order', 'action', 'previous_position', 'new_position', 'changed_by', 'changed_at']
    list_filter = ['action']
    readonly_fields = ['changed_at']
