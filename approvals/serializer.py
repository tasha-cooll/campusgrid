from rest_framework import serializers
from .models import Approval
from bookings.serializers import BookingSerializer


class ApprovalSerializer(serializers.ModelSerializer):
    booking_detail = BookingSerializer(source='booking', read_only=True)
    reviewed_by_name = serializers.CharField(
        source='reviewed_by.username',
        read_only=True
    )

    class Meta:
        model = Approval
        fields = [
            'id', 'booking', 'booking_detail', 'reviewed_by',
            'reviewed_by_name', 'decision', 'comments', 'reviewed_at'
        ]
        read_only_fields = ['id', 'reviewed_by', 'reviewed_at']


class ApprovalActionSerializer(serializers.Serializer):
    """Used for approve and reject actions."""
    comments = serializers.CharField(required=False, allow_blank=True)
