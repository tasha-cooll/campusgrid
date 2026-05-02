from django.contrib import admin
from .models import Booking, ConflictLog


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'facility', 'start_time',
                    'end_time', 'status', 'created_at']
    list_filter = ['status', 'facility']
    search_fields = ['user__username', 'facility__name', 'purpose']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ConflictLog)
class ConflictLogAdmin(admin.ModelAdmin):
    list_display = ['facility', 'requested_start',
                    'requested_end', 'detected_at', 'resolution']
    list_filter = ['facility']
    readonly_fields = ['detected_at']
