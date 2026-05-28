from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction

from .models import Emergency
from .forms import EmergencySubmitForm, EmergencyDecisionForm
from apps.members.views import admin_required
from apps.members.models import Member
from apps.cycles.models import Cycle
from apps.rotation.engine import RotationEngine
from apps.audit.utils import log_action
from apps.audit.models import AuditLog
from apps.notifications.utils import send_notification


@login_required
def emergency_list(request):
    user = request.user
    if user.is_admin:
        queryset = Emergency.objects.select_related(
            'member__user', 'cycle', 'decided_by'
        ).order_by('-requested_at')
        status_filter = request.GET.get('status', '')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
    else:
        try:
            member = user.member_profile
            queryset = Emergency.objects.filter(member=member).order_by('-requested_at')
        except Member.DoesNotExist:
            queryset = Emergency.objects.none()
        status_filter = ''

    context = {
        'emergencies': queryset,
        'status_filter': status_filter,
        'status_choices': Emergency.STATUS_CHOICES,
    }
    return render(request, 'emergencies/list.html', context)


@login_required
def emergency_submit(request):
    try:
        member = request.user.member_profile
    except Member.DoesNotExist:
        messages.error(request, "Profil membre introuvable.")
        return redirect('members:dashboard')

    active_cycle = Cycle.objects.filter(
        status__in=[Cycle.STATUS_OPEN, Cycle.STATUS_DISTRIBUTION]
    ).first()
    if not active_cycle:
        messages.error(request, "Aucun cycle actif pour soumettre une urgence.")
        return redirect('emergencies:list')

    # Vérifier une urgence par cycle
    existing = Emergency.objects.filter(
        member=member, cycle=active_cycle,
        status__in=[Emergency.STATUS_PENDING, Emergency.STATUS_APPROVED]
    ).first()
    if existing:
        messages.warning(request, "Vous avez déjà une demande d'urgence en cours pour ce cycle.")
        return redirect('emergencies:list')

    form = EmergencySubmitForm(request.POST or None, request.FILES or None)
    # Filtrer les têtes du membre
    form.fields['head'].queryset = member.heads.filter(is_active=True)
    form.fields['head'].required = False

    if request.method == 'POST' and form.is_valid():
        emergency = form.save(commit=False)
        emergency.member = member
        emergency.cycle = active_cycle
        emergency.save()

        log_action(request, AuditLog.ACTION_CREATE, 'Emergency', str(emergency.id), str(emergency))

        from apps.authentication.models import User
        for admin_user in User.objects.filter(role='admin'):
            send_notification(
                admin_user, 'Nouvelle demande d\'urgence',
                f"{member.full_name} a soumis une demande d'urgence pour le cycle {active_cycle.name}.",
                notification_type='warning', category='emergency'
            )
        messages.success(request, "Demande d'urgence soumise. En attente de validation.")
        return redirect('emergencies:list')

    return render(request, 'emergencies/submit.html', {
        'form': form, 'active_cycle': active_cycle, 'member': member
    })


@admin_required
def emergency_detail(request, pk):
    emergency = get_object_or_404(
        Emergency.objects.select_related('member__user', 'cycle', 'head', 'decided_by'), pk=pk
    )
    form = EmergencyDecisionForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        decision = form.cleaned_data['decision']
        emergency.decided_by = request.user
        emergency.decided_at = timezone.now()
        emergency.decision_notes = form.cleaned_data.get('decision_notes', '')

        if decision == EmergencyDecisionForm.DECISION_APPROVE:
            emergency.status = Emergency.STATUS_APPROVED
            new_position = form.cleaned_data['new_position']
            emergency.new_position = new_position

            try:
                engine = RotationEngine(emergency.cycle)
                engine.apply_emergency(emergency, new_position, request.user)
                msg = f"Votre demande d'urgence a été approuvée. Nouvelle position: {new_position}."
                notif_type = 'success'
            except Exception as e:
                messages.error(request, f"Erreur lors de la modification de rotation: {e}")
                return redirect('emergencies:detail', pk=pk)
        else:
            emergency.status = Emergency.STATUS_REFUSED
            msg = "Votre demande d'urgence a été refusée."
            notif_type = 'error'

        emergency.save()
        log_action(
            request, AuditLog.ACTION_APPROVE if decision == 'approve' else AuditLog.ACTION_REFUSE,
            'Emergency', str(emergency.id), str(emergency)
        )
        send_notification(emergency.member.user, 'Décision urgence', msg, notification_type=notif_type, category='emergency')
        messages.success(request, "Décision enregistrée.")
        return redirect('emergencies:list')

    return render(request, 'emergencies/detail.html', {'emergency': emergency, 'form': form})


@login_required
def emergency_my_status(request, pk):
    emergency = get_object_or_404(Emergency, pk=pk)
    if not request.user.is_admin and emergency.member.user != request.user:
        messages.error(request, "Accès non autorisé.")
        return redirect('emergencies:list')
    return render(request, 'emergencies/detail.html', {'emergency': emergency, 'readonly': True})
