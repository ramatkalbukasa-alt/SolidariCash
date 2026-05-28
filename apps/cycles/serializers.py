from rest_framework import serializers
from .models import Cycle


class CycleSerializer(serializers.ModelSerializer):
    total_collected = serializers.ReadOnlyField()
    commission_amount = serializers.ReadOnlyField()
    distributable_amount = serializers.ReadOnlyField()

    class Meta:
        model = Cycle
        fields = [
            'id', 'name', 'description', 'start_date', 'end_date',
            'contribution_amount', 'commission_rate', 'status',
            'total_collected', 'commission_amount', 'distributable_amount',
            'created_at', 'updated_at'
        ]
