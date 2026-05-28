from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Member, Head

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'first_name', 'last_name', 'email', 'phone', 'role']


class HeadSerializer(serializers.ModelSerializer):
    display_name = serializers.ReadOnlyField()

    class Meta:
        model = Head
        fields = ['id', 'head_number', 'label', 'display_name', 'status', 'is_active', 'created_at']


class MemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    heads = HeadSerializer(many=True, read_only=True)
    head_count = serializers.ReadOnlyField()
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Member
        fields = [
            'id', 'user', 'full_name', 'status', 'national_id',
            'head_count', 'heads', 'joined_at', 'updated_at'
        ]
