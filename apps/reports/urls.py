from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_index, name='index'),
    path('cycle/<int:cycle_id>/pdf/', views.export_cycle_pdf, name='cycle_pdf'),
    path('cycle/<int:cycle_id>/excel/', views.export_cycle_excel, name='cycle_excel'),
    path('receipt/<int:distribution_id>/pdf/', views.export_receipt_pdf, name='receipt_pdf'),
]
