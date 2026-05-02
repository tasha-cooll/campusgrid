from rest_framework import serializers
from .models import Facility, FacilityHours


class FacilityHoursSerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(
        source='get_day_of_week_display',
        read_only=True
    )

    class Meta:
        model = FacilityHours
        fields = ['id', 'day_of_week', 'day_name', 'open_time', 'close_time']


class FacilitySerializer(serializers.ModelSerializer):
    hours = FacilityHoursSerializer(many=True, read_only=True)

    class Meta:
        model = Facility
        fields = [
            'id', 'name', 'location', 'capacity',
            'description', 'is_active', 'hours',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FacilityWriteSerializer(serializers.ModelSerializer):
    """Used for create and update operations — excludes nested hours."""
    class Meta:
        model = Facility
        fields = ['id', 'name', 'location',
                  'capacity', 'description', 'is_active']
        read_only_fields = ['id']
