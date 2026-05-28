from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.contrib.auth import get_user_model

from .models import Member, Head
from .forms import MemberCreateForm, MemberUpdateForm, HeadAddForm, SuspendMemberForm
from apps.audit.utils import log_action
from apps.audit.models import AuditLog
from apps.cycles.models import Cycle
from apps.contributions.models import Contribution
from apps.rotation.models import RotationOrder
from apps.notifications.utils import send_notification

User = get_user_model()


def admin_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_admin:
            messages.error(request, "Accès réservé aux administrateurs.")
            return redirect('members:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
def dashboard(request):
    user = request.user
    if user.is_admin:
        return admin_dashboard(request)
    return member_dashboard(request)


def admin_dashboard(request):
    total_members = Member.objects.count()
    active_members = Member.objects.filter(status=Member.STATUS_ACTIVE).count()
    suspended_members = Member.objects.filter(status=Member.STATUS_SUSPENDED).count()
    total_heads = Head.objects.filter(is_active=True).count()
    
    active_cycle = Cycle.objects.filter(
        status__in=[Cycle.STATUS_OPEN, Cycle.STATUS_DISTRIBUTION]
    ).first()
    
    pending_contributions = 0
    total_collected = 0
    distribution_count = 0
    
    if active_cycle:
        pending_contributions = Contribution.objects.filter(
            cycle=active_cycle, status=Contribution.STATUS_PENDING
        ).count()
        total_collected = active_cycle.total_collected
        from apps.distributions.models import Distribution
        distribution_count = Distribution.objects.filter(
            cycle=active_cycle, status=Distribution.STATUS_COMPLETED
        ).count()
    
    from apps.emergencies.models import Emergency
    pending_emergencies = Emergency.objects.filter(status=Emergency.STATUS_PENDING).count()
    
    recent_members = Member.objects.select_related('user').order_by('-joined_at')[:5]
    
    context = {
        'total_members': total_members,
        'active_members': active_members,
        'suspended_members': suspended_members,
        'total_heads': total_heads,
        'active_cycle': active_cycle,
        'pending_contributions': pending_contributions,
        'total_collected': total_collected,
        'distribution_count': distribution_count,
        'pending_emergencies': pending_emergencies,
        'recent_members': recent_members,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


def member_dashboard(request):
    try:
        member = request.user.member_profile
    except Member.DoesNotExist:
        messages.warning(request, "Votre profil membre n'est pas encore configuré.")
        return render(request, 'dashboard/member_dashboard.html', {})
    
    active_cycle = Cycle.objects.filter(
        status__in=[Cycle.STATUS_OPEN, Cycle.STATUS_DISTRIBUTION]
    ).first()
    
    my_heads = member.heads.filter(is_active=True)
    my_contributions = []
    my_rotation_positions = []
    next_distribution = None
    
    if active_cycle:
        my_contributions = Contribution.objects.filter(
            head__in=my_heads, cycle=active_cycle
        ).select_related('head')
        
        my_rotation_positions = RotationOrder.objects.filter(
            head__in=my_heads, cycle=active_cycle
        ).order_by('position')
        
        next_distribution = RotationOrder.objects.filter(
            head__in=my_heads,
            cycle=active_cycle,
            status=RotationOrder.STATUS_PENDING
        ).order_by('position').first()
    
    recent_notifications = request.user.notifications.filter(is_read=False)[:5]
    
    context = {
        'member': member,
        'active_cycle': active_cycle,
        'my_heads': my_heads,
        'my_contributions': my_contributions,
        'my_rotation_positions': my_rotation_positions,
        'next_distribution': next_distribution,
        'recent_notifications': recent_notifications,
    }
    return render(request, 'dashboard/member_dashboard.html', context)


@admin_required
def member_list(request):
    queryset = Member.objects.select_related('user').annotate(
        heads_count=Count('heads', filter=Q(heads__is_active=True))
    )
    
    search = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    
    if search:
        queryset = queryset.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__email__icontains=search) |
            Q(user__username__icontains=search)
        )
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    
    paginator = Paginator(queryset, 15)
    page = paginator.get_page(request.GET.get('page'))
    
    context = {
        'members': page,
        'search': search,
        'status_filter': status_filter,
        'status_choices': Member.STATUS_CHOICES,
        'total_count': queryset.count(),
    }
    return render(request, 'members/list.html', context)


@admin_required
def member_create(request):
    form = MemberCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            data = form.cleaned_data
            user = User.objects.create_user(
                username=data['username'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                password=data['password'],
                phone=data.get('phone', ''),
                address=data.get('address', ''),
                role=User.ROLE_MEMBER,
            )
            member = Member.objects.create(
                user=user,
                national_id=data.get('national_id', ''),
            )
            head_count = data.get('head_count', 1)
            for i in range(1, head_count + 1):
                Head.objects.create(member=member, head_number=i)
            
            log_action(request, AuditLog.ACTION_CREATE, 'Member', str(member.id), str(member))
            send_notification(
                user, 'Bienvenue sur SolidariCash',
                f"Votre compte a été créé avec {head_count} tête(s). Bienvenue !",
                notification_type='success', category='system'
            )
            messages.success(request, f"Membre {user.full_name} créé avec {head_count} tête(s).")
            return redirect('members:detail', pk=member.pk)
    
    return render(request, 'members/form.html', {'form': form, 'action': 'Créer'})


@admin_required
def member_detail(request, pk):
    member = get_object_or_404(Member.objects.select_related('user'), pk=pk)
    heads = member.heads.all()
    active_cycle = Cycle.objects.filter(
        status__in=[Cycle.STATUS_OPEN, Cycle.STATUS_DISTRIBUTION]
    ).first()
    
    contributions = Contribution.objects.filter(
        head__member=member
    ).select_related('head', 'cycle').order_by('-created_at')[:20]
    
    rotation_orders = RotationOrder.objects.filter(
        head__member=member
    ).select_related('head', 'cycle').order_by('-cycle__start_date', 'position')[:20]
    
    from apps.emergencies.models import Emergency
    emergencies = Emergency.objects.filter(member=member).order_by('-requested_at')[:5]
    
    context = {
        'member': member,
        'heads': heads,
        'active_cycle': active_cycle,
        'contributions': contributions,
        'rotation_orders': rotation_orders,
        'emergencies': emergencies,
        'info_items': [],
    }
    return render(request, 'members/detail.html', context)


@admin_required
def member_update(request, pk):
    member = get_object_or_404(Member, pk=pk)
    form = MemberUpdateForm(request.POST or None, instance=member)
    if request.method == 'POST' and form.is_valid():
        form.save()
        user = member.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.phone = request.POST.get('phone', user.phone)
        user.save()
        log_action(request, AuditLog.ACTION_UPDATE, 'Member', str(member.id), str(member))
        messages.success(request, "Membre mis à jour avec succès.")
        return redirect('members:detail', pk=member.pk)
    
    return render(request, 'members/form.html', {'form': form, 'member': member, 'action': 'Modifier'})


@admin_required
def member_suspend(request, pk):
    member = get_object_or_404(Member, pk=pk)
    form = SuspendMemberForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        member.status = Member.STATUS_SUSPENDED
        member.suspended_at = timezone.now()
        member.suspension_reason = form.cleaned_data['reason']
        member.save()
        log_action(request, AuditLog.ACTION_SUSPEND, 'Member', str(member.id), str(member), {'reason': form.cleaned_data['reason']})
        send_notification(
            member.user, 'Compte suspendu',
            f"Votre compte a été suspendu. Motif : {form.cleaned_data['reason']}",
            notification_type='warning', category='system'
        )
        messages.warning(request, f"Membre {member.full_name} suspendu.")
        return redirect('members:detail', pk=member.pk)
    return render(request, 'members/suspend.html', {'form': form, 'member': member})


@admin_required
def member_activate(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        member.status = Member.STATUS_ACTIVE
        member.suspended_at = None
        member.suspension_reason = ''
        member.save()
        log_action(request, AuditLog.ACTION_UPDATE, 'Member', str(member.id), str(member))
        send_notification(
            member.user, 'Compte réactivé',
            "Votre compte a été réactivé. Vous pouvez maintenant participer normalement.",
            notification_type='success', category='system'
        )
        messages.success(request, f"Membre {member.full_name} réactivé.")
    return redirect('members:detail', pk=member.pk)


@admin_required
def member_add_head(request, pk):
    member = get_object_or_404(Member, pk=pk)
    form = HeadAddForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        count = form.cleaned_data['count']
        current_max = member.heads.aggregate(m=Count('id'))['m'] or 0
        with transaction.atomic():
            for i in range(1, count + 1):
                head_num = current_max + i
                Head.objects.create(member=member, head_number=head_num)
        log_action(request, AuditLog.ACTION_UPDATE, 'Member', str(member.id), str(member), {'heads_added': count})
        messages.success(request, f"{count} tête(s) ajoutée(s) à {member.full_name}.")
        return redirect('members:detail', pk=member.pk)
    return render(request, 'members/add_head.html', {'form': form, 'member': member})


@admin_required
def member_delete(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        user = member.user
        name = member.full_name
        log_action(request, AuditLog.ACTION_DELETE, 'Member', str(member.id), str(member))
        user.delete()
        messages.success(request, f"Membre {name} supprimé.")
        return redirect('members:list')
    return render(request, 'members/confirm_delete.html', {'member': member})


@login_required
def my_profile(request):
    try:
        member = request.user.member_profile
    except Member.DoesNotExist:
        messages.error(request, "Profil membre introuvable.")
        return redirect('members:dashboard')
    return redirect('members:detail', pk=member.pk)
