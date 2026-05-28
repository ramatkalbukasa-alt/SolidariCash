from django.contrib import admin
from .models import Cycle


@admin.register(Cycle)
class CycleAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'contribution_amount', 'status', 'created_by']
    list_filter = ['status']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at', 'closed_at']
