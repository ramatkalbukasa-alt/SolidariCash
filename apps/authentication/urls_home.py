from django.urls import path
from django.shortcuts import redirect


def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('members:dashboard')
    return redirect('auth:login')


urlpatterns = [
    path('', home_redirect, name='home'),
]
