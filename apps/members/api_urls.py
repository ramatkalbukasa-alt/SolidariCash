from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'', api_views.MemberViewSet, basename='member')

urlpatterns = router.urls
