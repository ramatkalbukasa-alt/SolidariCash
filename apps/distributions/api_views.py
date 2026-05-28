from rest_framework import viewsets, permissions
from .models import Distribution
from .serializers import DistributionSerializer


class DistributionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Distribution.objects.select_related('head__member__user', 'cycle').all()
    serializer_class = DistributionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'cycle']
