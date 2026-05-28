from rest_framework import viewsets, permissions
from .models import Emergency
from .serializers import EmergencySerializer


class EmergencyViewSet(viewsets.ModelViewSet):
    queryset = Emergency.objects.select_related('member__user', 'cycle').all()
    serializer_class = EmergencySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'cycle']
