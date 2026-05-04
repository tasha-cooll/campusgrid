from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'actor', 'action', 'booking', 'details']
    list_filter = ['action']
    search_fields = ['actor__username', 'details']
    readonly_fields = ['timestamp', 'actor', 'booking', 'action', 'details']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
