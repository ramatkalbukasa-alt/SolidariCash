from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Cycle
from .serializers import CycleSerializer


class CycleViewSet(viewsets.ModelViewSet):
    queryset = Cycle.objects.all()
    serializer_class = CycleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status']

    @action(detail=True, methods=['post'])
    def open(self, request, pk=None):
        cycle = self.get_object()
        cycle.status = Cycle.STATUS_OPEN
        cycle.save()
        return Response({'status': 'open'})

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        cycle = self.get_object()
        cycle.status = Cycle.STATUS_CLOSED
        cycle.save()
        return Response({'status': 'closed'})
