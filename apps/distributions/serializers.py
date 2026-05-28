from rest_framework import serializers
from .models import Distribution


class DistributionSerializer(serializers.ModelSerializer):
    head_display = serializers.ReadOnlyField(source='head.display_name')
    member_name = serializers.ReadOnlyField(source='head.member.full_name')
    cycle_name = serializers.ReadOnlyField(source='cycle.name')

    class Meta:
        model = Distribution
        fields = [
            'id', 'cycle', 'cycle_name', 'head', 'head_display', 'member_name',
            'gross_amount', 'commission_amount', 'net_amount',
            'status', 'processed_at', 'created_at'
        ]
