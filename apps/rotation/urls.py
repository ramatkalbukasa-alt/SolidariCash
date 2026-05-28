from django.urls import path
from . import views

app_name = 'rotation'

urlpatterns = [
    path('', views.rotation_view, name='view'),
    path('history/', views.rotation_history, name='history'),
    path('<int:pk>/reschedule/', views.reschedule_rotation, name='reschedule'),
]
