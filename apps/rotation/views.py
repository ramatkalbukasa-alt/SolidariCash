from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import RotationOrder, RotationHistory
from .engine import RotationEngine
from apps.members.views import admin_required
from apps.members.models import Member
from apps.cycles.models import Cycle
from apps.audit.utils import log_action
from apps.audit.models import AuditLog


@login_required
def rotation_view(request):
    user = request.user
    active_cycle = Cycle.objects.filter(
        status__in=[Cycle.STATUS_OPEN, Cycle.STATUS_DISTRIBUTION]
    ).first()

    cycle_id = request.GET.get('cycle')
    if cycle_id:
        selected_cycle = get_object_or_404(Cycle, pk=cycle_id)
    else:
        selected_cycle = active_cycle

    rotation_orders = RotationOrder.objects.none()
    if selected_cycle:
        rotation_orders = RotationOrder.objects.filter(
            cycle=selected_cycle
        ).select_related('head__member__user').order_by('position')

    if not user.is_admin:
        try:
            member = user.member_profile
            my_heads = member.heads.filter(is_active=True)
            my_positions = rotation_orders.filter(head__in=my_heads)
        except Member.DoesNotExist:
            my_positions = []
    else:
        my_positions = None

    cycles = Cycle.objects.all().order_by('-start_date')

    context = {
        'rotation_orders': rotation_orders,
        'selected_cycle': selected_cycle,
        'active_cycle': active_cycle,
        'cycles': cycles,
        'my_positions': my_positions,
    }
    return render(request, 'rotation/view.html', context)


@login_required
def rotation_history(request):
    user = request.user
    queryset = RotationHistory.objects.select_related(
        'rotation_order__head__member__user',
        'rotation_order__cycle',
        'changed_by'
    ).order_by('-changed_at')

    if not user.is_admin:
        try:
            member = user.member_profile
            queryset = queryset.filter(rotation_order__head__member=member)
        except Member.DoesNotExist:
            queryset = queryset.none()

    context = {'history': queryset[:50]}
    return render(request, 'rotation/history.html', context)


@admin_required
def reschedule_rotation(request, pk):
    rotation_order = get_object_or_404(RotationOrder, pk=pk)
    if request.method == 'POST':
        new_position = request.POST.get('new_position')
        reason = request.POST.get('reason', '')
        try:
            new_position = int(new_position)
            engine = RotationEngine(rotation_order.cycle)
            old = rotation_order.position
            rotation_order.position = new_position
            rotation_order.save()
            RotationHistory.objects.create(
                rotation_order=rotation_order,
                action=RotationHistory.ACTION_MODIFIED,
                previous_position=old,
                new_position=new_position,
                reason=reason,
                changed_by=request.user,
            )
            log_action(request, AuditLog.ACTION_UPDATE, 'RotationOrder', str(rotation_order.id), str(rotation_order))
            messages.success(request, "Position de rotation modifiée.")
        except (ValueError, TypeError):
            messages.error(request, "Position invalide.")
    return redirect('rotation:view')
