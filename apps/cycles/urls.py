from django.urls import path
from . import views

app_name = 'cycles'

urlpatterns = [
    path('', views.cycle_list, name='list'),
    path('create/', views.cycle_create, name='create'),
    path('<int:pk>/', views.cycle_detail, name='detail'),
    path('<int:pk>/update/', views.cycle_update, name='update'),
    path('<int:pk>/open/', views.cycle_open, name='open'),
    path('<int:pk>/generate-rotation/', views.cycle_generate_rotation, name='generate_rotation'),
    path('<int:pk>/close/', views.cycle_close, name='close'),
]
