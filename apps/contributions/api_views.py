from rest_framework import viewsets, permissions
from .models import Contribution
from .serializers import ContributionSerializer


class ContributionViewSet(viewsets.ModelViewSet):
    queryset = Contribution.objects.select_related('head__member__user', 'cycle').all()
    serializer_class = ContributionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'cycle']
