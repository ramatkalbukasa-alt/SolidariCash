from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction

from .models import Cycle
from .forms import CycleForm
from apps.members.views import admin_required
from apps.members.models import Member, Head
from apps.contributions.models import Contribution
from apps.rotation.engine import RotationEngine
from apps.audit.utils import log_action
from apps.audit.models import AuditLog
from apps.notifications.utils import send_bulk_notification


@admin_required
def cycle_list(request):
    cycles = Cycle.objects.all().order_by('-start_date')
    active_cycle = cycles.filter(status__in=[Cycle.STATUS_OPEN, Cycle.STATUS_DISTRIBUTION]).first()
    context = {'cycles': cycles, 'active_cycle': active_cycle}
    return render(request, 'cycles/list.html', context)


@admin_required
def cycle_create(request):
    form = CycleForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        cycle = form.save(commit=False)
        cycle.created_by = request.user
        cycle.save()
        log_action(request, AuditLog.ACTION_CREATE, 'Cycle', str(cycle.id), str(cycle))
        messages.success(request, f"Cycle '{cycle.name}' créé avec succès.")
        return redirect('cycles:detail', pk=cycle.pk)
    return render(request, 'cycles/form.html', {'form': form, 'action': 'Créer'})


@admin_required
def cycle_detail(request, pk):
    cycle = get_object_or_404(Cycle, pk=pk)
    from apps.rotation.models import RotationOrder
    from apps.distributions.models import Distribution
    
    rotation_orders = RotationOrder.objects.filter(
        cycle=cycle
    ).select_related('head__member__user').order_by('position')
    
    contributions = Contribution.objects.filter(
        cycle=cycle
    ).select_related('head__member__user').order_by('head__member__user__last_name')
    
    distributions = Distribution.objects.filter(
        cycle=cycle
    ).select_related('head__member__user').order_by('-processed_at')
    
    stats = {
        'total_contributions': contributions.count(),
        'paid_contributions': contributions.filter(status=Contribution.STATUS_PAID).count(),
        'pending_contributions': contributions.filter(status=Contribution.STATUS_PENDING).count(),
        'late_contributions': contributions.filter(status=Contribution.STATUS_LATE).count(),
        'total_collected': cycle.total_collected,
        'commission': cycle.commission_amount,
        'distributable': cycle.distributable_amount,
        'total_distributions': distributions.count(),
        'completed_distributions': distributions.filter(status='completed').count(),
    }
    
    context = {
        'cycle': cycle,
        'rotation_orders': rotation_orders,
        'contributions': contributions,
        'distributions': distributions,
        'stats': stats,
    }
    return render(request, 'cycles/detail.html', context)


@admin_required
def cycle_update(request, pk):
    cycle = get_object_or_404(Cycle, pk=pk)
    if cycle.status != Cycle.STATUS_PENDING:
        messages.error(request, "Un cycle ouvert ou clôturé ne peut pas être modifié.")
        return redirect('cycles:detail', pk=cycle.pk)
    form = CycleForm(request.POST or None, instance=cycle)
    if request.method == 'POST' and form.is_valid():
        form.save()
        log_action(request, AuditLog.ACTION_UPDATE, 'Cycle', str(cycle.id), str(cycle))
        messages.success(request, "Cycle mis à jour.")
        return redirect('cycles:detail', pk=cycle.pk)
    return render(request, 'cycles/form.html', {'form': form, 'cycle': cycle, 'action': 'Modifier'})


@admin_required
def cycle_open(request, pk):
    cycle = get_object_or_404(Cycle, pk=pk)
    if request.method == 'POST':
        if Cycle.objects.filter(status__in=[Cycle.STATUS_OPEN, Cycle.STATUS_DISTRIBUTION]).exclude(pk=pk).exists():
            messages.error(request, "Un cycle est déjà ouvert. Clôturez-le d'abord.")
            return redirect('cycles:detail', pk=pk)
        with transaction.atomic():
            cycle.status = Cycle.STATUS_OPEN
            cycle.save()
            _create_contributions_for_cycle(cycle)
        log_action(request, AuditLog.ACTION_UPDATE, 'Cycle', str(cycle.id), f"Cycle ouvert: {cycle.name}")
        send_bulk_notification(
            'Cycle ouvert — Contributions',
            "Les contributions du cycle sont ouvertes. Veuillez effectuer votre paiement.",
            notification_type='info', category='cycle'
        )
        messages.success(request, f"Cycle '{cycle.name}' ouvert. Contributions créées.")
    return redirect('cycles:detail', pk=pk)


def _create_contributions_for_cycle(cycle):
    active_heads = Head.objects.filter(
        is_active=True,
        member__status=Member.STATUS_ACTIVE
    ).select_related('member')
    
    for head in active_heads:
        Contribution.objects.get_or_create(
            head=head,
            cycle=cycle,
            defaults={'amount_due': cycle.contribution_amount}
        )


@admin_required
def cycle_generate_rotation(request, pk):
    cycle = get_object_or_404(Cycle, pk=pk)
    if request.method == 'POST':
        try:
            engine = RotationEngine(cycle)
            engine.generate()
            log_action(request, AuditLog.ACTION_UPDATE, 'Cycle', str(cycle.id), f"Rotation générée: {cycle.name}")
            messages.success(request, "Ordre de rotation généré avec succès.")
        except Exception as e:
            messages.error(request, f"Erreur lors de la génération : {str(e)}")
    return redirect('cycles:detail', pk=pk)


@admin_required
def cycle_close(request, pk):
    cycle = get_object_or_404(Cycle, pk=pk)
    if request.method == 'POST':
        cycle.status = Cycle.STATUS_CLOSED
        cycle.closed_at = timezone.now()
        cycle.save()
        log_action(request, AuditLog.ACTION_UPDATE, 'Cycle', str(cycle.id), f"Cycle clôturé: {cycle.name}")
        messages.success(request, f"Cycle '{cycle.name}' clôturé.")
    return redirect('cycles:detail', pk=pk)
