from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import LoginForm, UserUpdateForm, ChangePasswordForm
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
    form = UserUpdateForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        log_action(request, AuditLog.ACTION_UPDATE, 'User', str(request.user.id), str(request.user))
        messages.success(request, "Profil mis à jour avec succès.")
        return redirect('auth:profile')
    return render(request, 'auth/profile.html', {'form': form})


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
            messages.success(request, "Mot de passe modifié avec succès.")
            return redirect('auth:profile')
    return render(request, 'auth/change_password.html', {'form': form})
