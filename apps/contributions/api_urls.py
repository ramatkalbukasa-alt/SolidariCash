from django.urls import path
from rest_framework.routers import SimpleRouter
from . import api_views

router = SimpleRouter()
router.register(r'', api_views.ContributionViewSet, basename='contribution')
urlpatterns = router.urls
