from django.contrib import admin
from .models import Contribution


@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ['head', 'cycle', 'amount_due', 'amount_paid', 'status', 'submitted_at', 'validated_by']
    list_filter = ['status', 'cycle', 'payment_method']
    search_fields = ['head__member__user__first_name', 'head__member__user__last_name']
    readonly_fields = ['created_at', 'updated_at', 'validated_at']
