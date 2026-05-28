from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Member
from .serializers import MemberSerializer


class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.select_related('user').prefetch_related('heads').all()
    serializer_class = MemberSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    filterset_fields = ['status']

    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        member = self.get_object()
        member.status = Member.STATUS_SUSPENDED
        member.save()
        return Response({'status': 'suspended'})

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        member = self.get_object()
        member.status = Member.STATUS_ACTIVE
        member.save()
        return Response({'status': 'active'})
