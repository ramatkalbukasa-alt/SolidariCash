from django.contrib import admin
from .models import Distribution


@admin.register(Distribution)
class DistributionAdmin(admin.ModelAdmin):
    list_display = ['head', 'cycle', 'net_amount', 'status', 'processed_by', 'processed_at']
    list_filter = ['status', 'cycle']
    readonly_fields = ['created_at', 'updated_at']
