from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'full_name', 'email', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    fieldsets = UserAdmin.fieldsets + (
        ('Informations SolidariCash', {
            'fields': ('role', 'phone', 'address', 'avatar', 'is_2fa_enabled')
        }),
    )
