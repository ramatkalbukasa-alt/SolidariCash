from rest_framework import serializers
from .models import Emergency


class EmergencySerializer(serializers.ModelSerializer):
    member_name = serializers.ReadOnlyField(source='member.full_name')
    cycle_name = serializers.ReadOnlyField(source='cycle.name')

    class Meta:
        model = Emergency
        fields = [
            'id', 'member', 'member_name', 'cycle', 'cycle_name',
            'reason', 'status', 'requested_at', 'decided_at',
            'decision_notes', 'new_position'
        ]
