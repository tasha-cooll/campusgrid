from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'is_read', 'sent_at']
    list_filter = ['type', 'is_read']
    search_fields = ['user__username', 'message']
    readonly_fields = ['sent_at']
