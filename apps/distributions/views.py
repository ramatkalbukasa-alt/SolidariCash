from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from decimal import Decimal

from .models import Distribution
from apps.rotation.models import RotationOrder
from apps.contributions.models import Contribution
from apps.members.views import admin_required
from apps.members.models import Member
from apps.cycles.models import Cycle
from apps.audit.utils import log_action
from apps.audit.models import AuditLog
from apps.notifications.utils import send_notification


@login_required
def distribution_list(request):
    user = request.user
    if user.is_admin:
        queryset = Distribution.objects.select_related(
            'head__member__user', 'cycle', 'processed_by'
        ).order_by('-created_at')
    else:
        try:
            member = user.member_profile
            queryset = Distribution.objects.filter(
                head__member=member
            ).select_related('head', 'cycle').order_by('-created_at')
        except Member.DoesNotExist:
            queryset = Distribution.objects.none()

    cycle_filter = request.GET.get('cycle', '')
    if cycle_filter:
        queryset = queryset.filter(cycle_id=cycle_filter)

    cycles = Cycle.objects.all().order_by('-start_date')
    context = {
        'distributions': queryset[:50],
        'cycles': cycles,
        'cycle_filter': cycle_filter,
    }
    return render(request, 'distributions/list.html', context)


@admin_required
def distribution_process(request, rotation_order_id):
    """Traiter une distribution pour un ordre de rotation donné."""
    rotation_order = get_object_or_404(
        RotationOrder.objects.select_related('head__member__user', 'cycle'),
        pk=rotation_order_id
    )
    cycle = rotation_order.cycle
    head = rotation_order.head

    # Vérifications d'éligibilité
    if rotation_order.status == RotationOrder.STATUS_SERVED:
        messages.error(request, "Cette tête a déjà été servie.")
        return redirect('distributions:list')

    contribution = Contribution.objects.filter(
        head=head, cycle=cycle
    ).first()
    if not contribution or contribution.status != Contribution.STATUS_PAID:
        messages.error(request, f"{head.member.full_name} n'a pas payé sa contribution pour ce cycle.")
        return redirect('distributions:list')

    if head.member.status != Member.STATUS_ACTIVE:
        messages.error(request, f"{head.member.full_name} est suspendu(e) et ne peut pas recevoir de distribution.")
        return redirect('distributions:list')

    if Distribution.objects.filter(rotation_order=rotation_order, status=Distribution.STATUS_COMPLETED).exists():
        messages.error(request, "Une distribution a déjà été effectuée pour cet ordre.")
        return redirect('distributions:list')

    if request.method == 'POST':
        with transaction.atomic():
            # Calculer les montants
            gross = cycle.total_collected
            commission = gross * cycle.commission_rate
            net = gross - commission

            dist = Distribution.objects.create(
                rotation_order=rotation_order,
                cycle=cycle,
                head=head,
                gross_amount=gross,
                commission_amount=commission,
                net_amount=net,
                status=Distribution.STATUS_COMPLETED,
                processed_by=request.user,
                processed_at=timezone.now(),
                notes=request.POST.get('notes', ''),
            )

            rotation_order.status = RotationOrder.STATUS_SERVED
            rotation_order.save()

            log_action(
                request, AuditLog.ACTION_DISTRIBUTE, 'Distribution',
                str(dist.id), str(dist),
                {'net_amount': str(net), 'head': str(head)}
            )
            send_notification(
                head.member.user,
                'Distribution effectuée',
                f"Une distribution de {net} a été effectuée pour votre tête '{head.display_name}'.",
                notification_type='success', category='distribution'
            )
            messages.success(request, f"Distribution effectuée pour {head.member.full_name}. Montant net: {net}")
            return redirect('distributions:list')

    context = {
        'rotation_order': rotation_order,
        'cycle': cycle,
        'head': head,
        'contribution': contribution,
        'gross': cycle.total_collected,
        'commission': cycle.commission_amount,
        'net': cycle.distributable_amount,
    }
    return render(request, 'distributions/process.html', context)


@admin_required
def distribution_fail(request, pk):
    """Marquer une distribution comme échouée."""
    distribution = get_object_or_404(Distribution, pk=pk)
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        distribution.status = Distribution.STATUS_FAILED
        distribution.failure_reason = reason
        distribution.save()
        distribution.rotation_order.status = RotationOrder.STATUS_PENDING
        distribution.rotation_order.save()
        log_action(request, AuditLog.ACTION_UPDATE, 'Distribution', str(distribution.id), str(distribution))
        messages.warning(request, "Distribution marquée comme échouée. Reprogrammation nécessaire.")
    return redirect('distributions:list')
