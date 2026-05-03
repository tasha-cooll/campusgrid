from django.contrib import admin
from .models import Facility, FacilityHours, FacilityZone, RecurringBlock


class FacilityHoursInline(admin.TabularInline):
    model = FacilityHours
    extra = 3
    fields = ['day_of_week', 'open_time', 'close_time']


class FacilityZoneInline(admin.TabularInline):
    model = FacilityZone
    extra = 2
    fields = ['name', 'capacity', 'description', 'is_active']


class RecurringBlockInline(admin.TabularInline):
    model = RecurringBlock
    extra = 1
    fields = ['label', 'zone', 'day_of_week',
              'start_time', 'end_time', 'is_active']


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'capacity', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'location']
    inlines = [FacilityZoneInline, FacilityHoursInline, RecurringBlockInline]


@admin.register(FacilityZone)
class FacilityZoneAdmin(admin.ModelAdmin):
    list_display = ['facility', 'name', 'capacity', 'is_active']
    list_filter = ['facility', 'is_active']


@admin.register(RecurringBlock)
class RecurringBlockAdmin(admin.ModelAdmin):
    list_display = ['label', 'facility', 'zone',
                    'day_of_week', 'start_time', 'end_time', 'is_active']
    list_filter = ['facility', 'day_of_week', 'is_active']
    search_fields = ['label']


@admin.register(FacilityHours)
class FacilityHoursAdmin(admin.ModelAdmin):
    list_display = ['facility', 'day_of_week', 'open_time', 'close_time']
    list_filter = ['facility', 'day_of_week']
