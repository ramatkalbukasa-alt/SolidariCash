from django.urls import path
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'', api_views.ContributionViewSet, basename='contribution')
urlpatterns = router.urls
