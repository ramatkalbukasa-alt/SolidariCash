from rest_framework import serializers
from .models import Contribution


class ContributionSerializer(serializers.ModelSerializer):
    head_display = serializers.ReadOnlyField(source='head.display_name')
    cycle_name = serializers.ReadOnlyField(source='cycle.name')
    member_name = serializers.ReadOnlyField(source='head.member.full_name')

    class Meta:
        model = Contribution
        fields = [
            'id', 'head', 'head_display', 'member_name', 'cycle', 'cycle_name',
            'amount_due', 'amount_paid', 'payment_method', 'payment_reference',
            'status', 'submitted_at', 'validated_at', 'created_at'
        ]
