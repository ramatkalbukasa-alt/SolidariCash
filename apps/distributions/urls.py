from django.urls import path
from . import views

app_name = 'distributions'

urlpatterns = [
    path('', views.distribution_list, name='list'),
    path('process/<int:rotation_order_id>/', views.distribution_process, name='process'),
    path('<int:pk>/fail/', views.distribution_fail, name='fail'),
]
