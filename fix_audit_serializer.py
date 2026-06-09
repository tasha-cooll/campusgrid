content = """\
from rest_framework import serializers
from reports.models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    actor_name       = serializers.SerializerMethodField()
    action_display   = serializers.SerializerMethodField()
    booking_info     = serializers.SerializerMethodField()
    target_user_name = serializers.SerializerMethodField()
    ip_address       = serializers.SerializerMethodField()

    class Meta:
        model  = AuditLog
        fields = [
            'id', 'actor_name', 'action', 'action_display',
            'details', 'booking_info', 'target_user_name',
            'ip_address', 'timestamp'
        ]

    def get_actor_name(self, obj):
        return obj.actor.username if obj.actor else 'System'

    def get_action_display(self, obj):
        return obj.get_action_display()

    def get_booking_info(self, obj):
        if not obj.booking:
            return None
        return {
            'id':       obj.booking.id,
            'facility': obj.booking.facility.name,
            'purpose':  obj.booking.purpose,
        }

    def get_target_user_name(self, obj):
        return obj.target_user.username if obj.target_user else None

    def get_ip_address(self, obj):
        return str(obj.ip_address) if obj.ip_address else None
"""

with open('reports/serializers.py', 'w', encoding='utf-8', newline='\\n') as f:
    f.write(content)
print('Serializer written successfully')