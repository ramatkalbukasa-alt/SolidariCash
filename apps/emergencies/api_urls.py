from django.urls import path
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'', api_views.EmergencyViewSet, basename='emergency')
urlpatterns = router.urls
