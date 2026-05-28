from rest_framework import viewsets, permissions
from .models import RotationOrder
from .serializers import RotationOrderSerializer


class RotationOrderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RotationOrder.objects.select_related('head__member__user', 'cycle').all()
    serializer_class = RotationOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['cycle', 'status']
