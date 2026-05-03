from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(
        source='get_type_display',
        read_only=True
    )

    class Meta:
        model = Notification
        fields = [
            'id', 'booking', 'type', 'type_display',
            'message', 'is_read', 'sent_at'
        ]
        read_only_fields = ['id', 'sent_at']
