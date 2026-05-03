from django.contrib import admin
from .models import Approval


@admin.register(Approval)
class ApprovalAdmin(admin.ModelAdmin):
    list_display = ['booking', 'reviewed_by', 'decision', 'reviewed_at']
    list_filter = ['decision']
    search_fields = ['booking__user__username', 'booking__facility__name']
    readonly_fields = ['reviewed_at']
