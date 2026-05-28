from django.urls import path
from . import views

app_name = 'contributions'

urlpatterns = [
    path('', views.contribution_list, name='list'),
    path('<int:pk>/submit/', views.contribution_submit, name='submit'),
    path('<int:pk>/validate/', views.contribution_validate, name='validate'),
    path('<int:pk>/', views.contribution_detail, name='detail'),
]
