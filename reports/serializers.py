from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source='actor.username', read_only=True)
    actor_id = serializers.CharField(
        source='actor.institutional_id', read_only=True)
    action_display = serializers.CharField(
        source='get_action_display', read_only=True)
    booking_info = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = [
            'id', 'actor', 'actor_name', 'actor_id',
            'booking', 'booking_info', 'action', 'action_display',
            'details', 'timestamp'
        ]

    def get_booking_info(self, obj):
        if obj.booking:
            return {
                'id':       obj.booking.id,
                'facility': obj.booking.facility.name,
                'status':   obj.booking.status,
            }
        return None
