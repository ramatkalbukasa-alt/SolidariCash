import os
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import LoginForm, UserUpdateForm, AvatarUpdateForm, ChangePasswordForm
from apps.audit.utils import log_action
from apps.audit.models import AuditLog


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('members:dashboard')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        log_action(request, AuditLog.ACTION_LOGIN, 'User', str(user.id), str(user))
        messages.success(request, f"Bienvenue, {user.full_name} !")
        next_url = request.GET.get('next', 'members:dashboard')
        return redirect(next_url)

    return render(request, 'auth/login.html', {'form': form})


@login_required
def logout_view(request):
    log_action(request, AuditLog.ACTION_LOGOUT, 'User', str(request.user.id), str(request.user))
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('auth:login')


@login_required
def profile_view(request):
    user = request.user
    info_form = UserUpdateForm(instance=user)
    avatar_form = AvatarUpdateForm(instance=user)

    if request.method == 'POST':
        if 'save_info' in request.POST:
            info_form = UserUpdateForm(request.POST, instance=user)
            if info_form.is_valid():
                info_form.save()
                log_action(request, AuditLog.ACTION_UPDATE, 'User', str(user.id), str(user),
                           {'fields': list(info_form.changed_data)})
                messages.success(request, "Informations mises à jour avec succès.")
                return redirect('auth:profile')

        elif 'save_avatar' in request.POST:
            avatar_form = AvatarUpdateForm(request.POST, request.FILES, instance=user)
            if avatar_form.is_valid():
                # Supprimer l'ancienne photo avant la sauvegarde
                if user.avatar and 'avatar' in avatar_form.changed_data:
                    old_path = user.avatar.path
                    if os.path.isfile(old_path):
                        os.remove(old_path)
                avatar_form.save()
                log_action(request, AuditLog.ACTION_UPDATE, 'User', str(user.id), str(user),
                           {'action': 'avatar_updated'})
                messages.success(request, "Photo de profil mise à jour.")
                return redirect('auth:profile')

    # Infos membre associé
    member = None
    try:
        member = user.member_profile
    except Exception:
        pass

    context = {
        'info_form': info_form,
        'avatar_form': avatar_form,
        'member': member,
    }
    return render(request, 'auth/profile.html', context)


@login_required
@require_http_methods(["POST"])
def avatar_delete_view(request):
    user = request.user
    if user.avatar:
        old_path = user.avatar.path
        if os.path.isfile(old_path):
            os.remove(old_path)
        user.avatar = None
        user.save(update_fields=['avatar'])
        log_action(request, AuditLog.ACTION_UPDATE, 'User', str(user.id), str(user),
                   {'action': 'avatar_deleted'})
        messages.success(request, "Photo de profil supprimée.")
    return redirect('auth:profile')


@login_required
def change_password_view(request):
    form = ChangePasswordForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = request.user
        if not user.check_password(form.cleaned_data['old_password']):
            form.add_error('old_password', 'Mot de passe actuel incorrect.')
        else:
            user.set_password(form.cleaned_data['new_password1'])
            user.save()
            update_session_auth_hash(request, user)
            log_action(request, AuditLog.ACTION_UPDATE, 'User', str(user.id), str(user),
                       {'action': 'password_changed'})
            messages.success(request, "Mot de passe modifié avec succès.")
            return redirect('auth:profile')
    return render(request, 'auth/change_password.html', {'form': form})
