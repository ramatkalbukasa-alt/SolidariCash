from rest_framework import serializers
from .models import RotationOrder, RotationHistory


class RotationOrderSerializer(serializers.ModelSerializer):
    head_display = serializers.ReadOnlyField(source='head.display_name')
    member_name = serializers.ReadOnlyField(source='head.member.full_name')
    cycle_name = serializers.ReadOnlyField(source='cycle.name')

    class Meta:
        model = RotationOrder
        fields = [
            'id', 'cycle', 'cycle_name', 'head', 'head_display', 'member_name',
            'position', 'original_position', 'status', 'is_emergency',
            'scheduled_date', 'created_at'
        ]
