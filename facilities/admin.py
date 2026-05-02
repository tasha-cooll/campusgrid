from django.contrib import admin
from .models import Facility, FacilityHours


class FacilityHoursInline(admin.TabularInline):
    model = FacilityHours
    extra = 3
    fields = ['day_of_week', 'open_time', 'close_time']


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'capacity', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'location']
    inlines = [FacilityHoursInline]


@admin.register(FacilityHours)
class FacilityHoursAdmin(admin.ModelAdmin):
    list_display = ['facility', 'day_of_week', 'open_time', 'close_time']
    list_filter = ['facility', 'day_of_week']
