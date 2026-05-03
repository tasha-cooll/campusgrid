from rest_framework import serializers
from django.utils import timezone
from .models import Booking, ConflictLog
from facilities.serializers import FacilitySerializer
from accounts.serializers import UserSerializer


class BookingSerializer(serializers.ModelSerializer):
    facility_detail = FacilitySerializer(source='facility', read_only=True)
    user_detail = UserSerializer(source='user', read_only=True)
    status_display = serializers.CharField(
        source='get_status_display', read_only=True)
    zone_name = serializers.CharField(source='zone.name', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'user_detail', 'facility', 'facility_detail',
            'zone', 'zone_name', 'start_time', 'end_time', 'purpose',
            'expected_attendance', 'status', 'status_display',
            'is_priority', 'priority_reason', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'status', 'created_at', 'updated_at']


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            'id', 'facility', 'zone', 'start_time', 'end_time',
            'purpose', 'expected_attendance', 'notes',
            'is_priority', 'priority_reason'
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        if attrs['end_time'] <= attrs['start_time']:
            raise serializers.ValidationError({
                "end_time": "End time must be after start time."
            })
        if attrs['start_time'] < timezone.now():
            raise serializers.ValidationError({
                "start_time": "Cannot book a slot in the past."
            })
        # Validate zone belongs to facility
        zone = attrs.get('zone', None)
        facility = attrs.get('facility')
        if zone and zone.facility != facility:
            raise serializers.ValidationError({
                "zone": "This zone does not belong to the selected facility."
            })
        return attrs


class ConflictCheckSerializer(serializers.Serializer):
    facility_id = serializers.IntegerField()
    zone_id = serializers.IntegerField(required=False, allow_null=True)
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()


class ConflictLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConflictLog
        fields = [
            'id', 'facility', 'zone', 'requested_start',
            'requested_end', 'detected_at', 'resolution'
        ]
