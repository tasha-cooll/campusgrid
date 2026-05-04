from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = [
        'institutional_id', 'get_full_name', 'email',
        'role', 'is_active', 'must_change_password', 'date_joined'
    ]
    list_filter = ['role', 'is_active', 'must_change_password']
    search_fields = ['institutional_id', 'username',
                     'email', 'first_name', 'last_name']
    list_editable = ['role']
    ordering = ['-date_joined']

    fieldsets = (
        # Login credentials
        (None, {
            'fields': ('username', 'password')
        }),
        # Personal info
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        # Institutional identity
        ('Institutional Identity', {
            'fields': ('institutional_id', 'role'),
            'description': (
                'Set the Student ID or Staff ID as the institutional identifier. '
                'Assign role: Requester (club leaders/coaches), '
                'Approver (Sports Director), Admin (system administrator).'
            )
        }),
        # Account control
        ('Account Control', {
            'fields': ('is_active', 'must_change_password'),
            'description': (
                'Deactivate accounts here. '
                'Check "Must change password" to force a password reset on next login.'
            )
        }),
        # Permissions — collapsed by default
        ('Permissions', {
            'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        # Dates
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )

    add_fieldsets = (
        # When creating a new user from admin
        (None, {
            'classes': ('wide',),
            'fields': (
                'institutional_id', 'username',
                'first_name', 'last_name',
                'email', 'phone', 'role',
                'password1', 'password2',
                'must_change_password', 'is_active'
            ),
            'description': (
                'Create a new user account. Set a temporary password — '
                'the user should change it on first login. '
                'Use the Student ID or Staff ID as the Institutional ID.'
            )
        }),
    )

    readonly_fields = ['last_login', 'date_joined']

    # Admin action — reset password flag
    actions = ['force_password_change']

    def force_password_change(self, request, queryset):
        updated = queryset.update(must_change_password=True)
        self.message_user(
            request,
            f"{updated} user(s) flagged to change password on next login."
        )
    force_password_change.short_description = "Flag selected users to change password"
