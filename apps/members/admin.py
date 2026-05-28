from django.contrib import admin
from .models import Member, Head


class HeadInline(admin.TabularInline):
    model = Head
    extra = 1
    fields = ['head_number', 'label', 'status', 'is_active']


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'get_email', 'status', 'head_count', 'joined_at']
    list_filter = ['status', 'joined_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    inlines = [HeadInline]
    readonly_fields = ['joined_at', 'updated_at']

    @admin.display(description='Email')
    def get_email(self, obj):
        return obj.user.email


@admin.register(Head)
class HeadAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'member', 'head_number', 'status', 'is_active']
    list_filter = ['status', 'is_active']
    search_fields = ['member__user__first_name', 'member__user__last_name']
