from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Contribution
from .forms import ContributionPaymentForm, ContributionValidateForm
from apps.members.views import admin_required
from apps.members.models import Member
from apps.cycles.models import Cycle
from apps.audit.utils import log_action
from apps.audit.models import AuditLog
from apps.notifications.utils import send_notification


@login_required
def contribution_list(request):
    user = request.user
    if user.is_admin:
        queryset = Contribution.objects.select_related(
            'head__member__user', 'cycle'
        ).order_by('-created_at')
    else:
        try:
            member = user.member_profile
        except Member.DoesNotExist:
            return render(request, 'contributions/list.html', {'contributions': []})
        queryset = Contribution.objects.filter(
            head__member=member
        ).select_related('head', 'cycle').order_by('-created_at')

    cycle_filter = request.GET.get('cycle', '')
    status_filter = request.GET.get('status', '')

    if cycle_filter:
        queryset = queryset.filter(cycle_id=cycle_filter)
    if status_filter:
        queryset = queryset.filter(status=status_filter)

    paginator = Paginator(queryset, 20)
    page = paginator.get_page(request.GET.get('page'))
    cycles = Cycle.objects.all().order_by('-start_date')

    context = {
        'contributions': page,
        'cycles': cycles,
        'cycle_filter': cycle_filter,
        'status_filter': status_filter,
        'status_choices': Contribution.STATUS_CHOICES,
    }
    return render(request, 'contributions/list.html', context)


@login_required
def contribution_submit(request, pk):
    contribution = get_object_or_404(Contribution, pk=pk)
    if not request.user.is_admin:
        try:
            member = request.user.member_profile
            if contribution.head.member != member:
                messages.error(request, "Accès non autorisé.")
                return redirect('contributions:list')
        except Member.DoesNotExist:
            messages.error(request, "Profil membre introuvable.")
            return redirect('contributions:list')

    if contribution.status == Contribution.STATUS_PAID:
        messages.info(request, "Cette contribution est déjà payée.")
        return redirect('contributions:list')

    form = ContributionPaymentForm(request.POST or None, request.FILES or None, instance=contribution)
    if request.method == 'POST' and form.is_valid():
        c = form.save(commit=False)
        c.status = Contribution.STATUS_PENDING
        c.submitted_at = timezone.now()
        c.save()
        log_action(request, AuditLog.ACTION_UPDATE, 'Contribution', str(c.id), str(c))
        send_notification(
            request.user, 'Paiement soumis',
            f"Votre paiement pour {contribution.cycle.name} a été soumis et attend validation.",
            notification_type='info', category='contribution'
        )
        from apps.authentication.models import User
        admins = User.objects.filter(role='admin')
        for admin_user in admins:
            send_notification(
                admin_user, 'Nouveau paiement à valider',
                f"{contribution.head.member.full_name} a soumis un paiement pour {contribution.cycle.name}.",
                notification_type='info', category='contribution'
            )
        messages.success(request, "Paiement soumis. En attente de validation.")
        return redirect('contributions:list')

    context = {'form': form, 'contribution': contribution}
    return render(request, 'contributions/submit.html', context)


@admin_required
def contribution_validate(request, pk):
    contribution = get_object_or_404(
        Contribution.objects.select_related('head__member__user', 'cycle'), pk=pk
    )
    form = ContributionValidateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        decision = form.cleaned_data['decision']
        contribution.validated_by = request.user
        contribution.validated_at = timezone.now()
        contribution.admin_notes = form.cleaned_data.get('admin_notes', '')

        if decision == ContributionValidateForm.DECISION_APPROVE:
            contribution.status = Contribution.STATUS_PAID
            msg = "Votre contribution a été validée."
            notif_type = 'success'
        elif decision == ContributionValidateForm.DECISION_REJECT:
            contribution.status = Contribution.STATUS_REJECTED
            msg = "Votre contribution a été rejetée. Contactez l'administrateur."
            notif_type = 'error'
        else:
            contribution.status = Contribution.STATUS_LATE
            msg = "Votre contribution est marquée en retard."
            notif_type = 'warning'

        contribution.save()
        log_action(request, AuditLog.ACTION_VALIDATE, 'Contribution', str(contribution.id), str(contribution))
        send_notification(contribution.head.member.user, 'Statut de contribution', msg, notification_type=notif_type, category='contribution')
        messages.success(request, "Décision enregistrée.")
        return redirect('contributions:list')

    context = {'form': form, 'contribution': contribution}
    return render(request, 'contributions/validate.html', context)


@login_required
def contribution_detail(request, pk):
    contribution = get_object_or_404(
        Contribution.objects.select_related('head__member__user', 'cycle', 'validated_by'), pk=pk
    )
    if not request.user.is_admin:
        try:
            member = request.user.member_profile
            if contribution.head.member != member:
                messages.error(request, "Accès non autorisé.")
                return redirect('contributions:list')
        except Member.DoesNotExist:
            pass
    return render(request, 'contributions/detail.html', {'contribution': contribution})
