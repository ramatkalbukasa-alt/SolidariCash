from django.urls import path
from . import views

app_name = 'emergencies'

urlpatterns = [
    path('', views.emergency_list, name='list'),
    path('submit/', views.emergency_submit, name='submit'),
    path('<int:pk>/', views.emergency_detail, name='detail'),
    path('<int:pk>/status/', views.emergency_my_status, name='status'),
]
