from rest_framework import serializers
from django.utils import timezone
from .models import Booking, ConflictLog
from facilities.serializers import FacilitySerializer
from accounts.serializers import UserSerializer


class BookingSerializer(serializers.ModelSerializer):
    """Full read serializer — includes nested facility and user info."""
    facility_detail = FacilitySerializer(source='facility', read_only=True)
    user_detail = UserSerializer(source='user', read_only=True)
    status_display = serializers.CharField(
        source='get_status_display', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'user_detail', 'facility', 'facility_detail',
            'start_time', 'end_time', 'purpose', 'expected_attendance',
            'status', 'status_display', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'status', 'created_at', 'updated_at']


class BookingCreateSerializer(serializers.ModelSerializer):
    """Write serializer — used when submitting a new booking request."""
    class Meta:
        model = Booking
        fields = [
            'id', 'facility', 'start_time', 'end_time',
            'purpose', 'expected_attendance', 'notes'
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        # End time must be after start time
        if attrs['end_time'] <= attrs['start_time']:
            raise serializers.ValidationError({
                "end_time": "End time must be after start time."
            })
        # Cannot book in the past
        if attrs['start_time'] < timezone.now():
            raise serializers.ValidationError({
                "start_time": "Cannot book a slot in the past."
            })
        return attrs


class ConflictCheckSerializer(serializers.Serializer):
    """Used by the conflict check endpoint before booking submission."""
    facility_id = serializers.IntegerField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()


class ConflictLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConflictLog
        fields = [
            'id', 'facility', 'requested_start', 'requested_end',
            'detected_at', 'resolution'
        ]
