from django.db import models
from django.conf import settings


class DayOfWeek(models.IntegerChoices):
    MONDAY = 0, 'Monday'
    TUESDAY = 1, 'Tuesday'
    WEDNESDAY = 2, 'Wednesday'
    THURSDAY = 3, 'Thursday'
    FRIDAY = 4, 'Friday'
    SATURDAY = 5, 'Saturday'
    SUNDAY = 6, 'Sunday'


class Facility(models.Model):
    name = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=200)
    capacity = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Facilities'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (capacity: {self.capacity})"


class FacilityZone(models.Model):
    """
    A bookable section within a facility.
    e.g. Main Sports Field → Basketball Court, Football Pitch
    If a facility has no zones defined, the whole facility is booked.
    """
    facility = models.ForeignKey(
        Facility,
        on_delete=models.CASCADE,
        related_name='zones'
    )
    name = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['facility', 'name']
        ordering = ['facility', 'name']

    def __str__(self):
        return f"{self.facility.name} — {self.name} (cap: {self.capacity})"


class FacilityHours(models.Model):
    facility = models.ForeignKey(
        Facility,
        on_delete=models.CASCADE,
        related_name='hours'
    )
    day_of_week = models.IntegerField(choices=DayOfWeek.choices)
    open_time = models.TimeField()
    close_time = models.TimeField()

    class Meta:
        verbose_name_plural = 'Facility Hours'
        unique_together = ['facility', 'day_of_week']
        ordering = ['day_of_week']

    def __str__(self):
        return f"{self.facility.name} — {self.get_day_of_week_display()} {self.open_time}–{self.close_time}"


class RecurringBlock(models.Model):
    """
    A permanently blocked time slot on a facility or zone.
    e.g. Chapel Service every Sunday 09:00–12:00.
    Cannot be booked by anyone except Admin creating a priority booking.
    """
    facility = models.ForeignKey(
        Facility,
        on_delete=models.CASCADE,
        related_name='recurring_blocks'
    )
    zone = models.ForeignKey(
        FacilityZone,
        on_delete=models.CASCADE,
        related_name='recurring_blocks',
        null=True, blank=True,
        help_text="Leave blank to block the entire facility"
    )
    label = models.CharField(
        max_length=100,
        help_text="e.g. Chapel Service, Weekly Staff Meeting"
    )
    day_of_week = models.IntegerField(choices=DayOfWeek.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recurring_blocks_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        zone_str = f" ({self.zone.name})" if self.zone else " (entire facility)"
        return f"{self.label} — {self.facility.name}{zone_str} every {self.get_day_of_week_display()} {self.start_time}–{self.end_time}"
