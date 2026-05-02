from django.db import models


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
