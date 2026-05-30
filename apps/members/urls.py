from django.urls import path
from . import views

app_name = 'members'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('list/', views.member_list, name='list'),
    path('create/', views.member_create, name='create'),
    path('<int:pk>/', views.member_detail, name='detail'),
    path('<int:pk>/update/', views.member_update, name='update'),
    path('<int:pk>/suspend/', views.member_suspend, name='suspend'),
    path('<int:pk>/activate/', views.member_activate, name='activate'),
    path('<int:pk>/add-head/', views.member_add_head, name='add_head'),
    path('<int:pk>/delete/', views.member_delete, name='delete'),
    path('profile/', views.my_profile, name='my_profile'),
    path('analytics/', views.analytics, name='analytics'),
]
