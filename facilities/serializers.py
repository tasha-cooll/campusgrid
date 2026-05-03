from rest_framework import serializers
from .models import Facility, FacilityZone, FacilityHours, RecurringBlock


class FacilityHoursSerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(
        source='get_day_of_week_display',
        read_only=True
    )

    class Meta:
        model = FacilityHours
        fields = ['id', 'day_of_week', 'day_name', 'open_time', 'close_time']


class FacilityZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacilityZone
        fields = ['id', 'facility', 'name',
                  'capacity', 'description', 'is_active']
        read_only_fields = ['id']


class RecurringBlockSerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(
        source='get_day_of_week_display',
        read_only=True
    )
    created_by_name = serializers.CharField(
        source='created_by.username',
        read_only=True
    )

    class Meta:
        model = RecurringBlock
        fields = [
            'id', 'facility', 'zone', 'label', 'day_of_week', 'day_name',
            'start_time', 'end_time', 'is_active', 'created_by',
            'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at']


class FacilitySerializer(serializers.ModelSerializer):
    hours = FacilityHoursSerializer(many=True, read_only=True)
    zones = FacilityZoneSerializer(many=True, read_only=True)
    recurring_blocks = RecurringBlockSerializer(many=True, read_only=True)

    class Meta:
        model = Facility
        fields = [
            'id', 'name', 'location', 'capacity', 'description',
            'is_active', 'hours', 'zones', 'recurring_blocks',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FacilityWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = ['id', 'name', 'location',
                  'capacity', 'description', 'is_active']
        read_only_fields = ['id']
