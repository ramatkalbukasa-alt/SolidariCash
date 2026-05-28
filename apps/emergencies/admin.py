from django.contrib import admin
from .models import Emergency


@admin.register(Emergency)
class EmergencyAdmin(admin.ModelAdmin):
    list_display = ['member', 'cycle', 'status', 'requested_at', 'decided_by', 'decided_at']
    list_filter = ['status', 'cycle']
    readonly_fields = ['requested_at', 'decided_at']
