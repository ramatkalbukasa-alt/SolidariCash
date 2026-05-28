from django.urls import path, include
from rest_framework.routers import SimpleRouter
from . import api_views

router = SimpleRouter()
router.register(r'', api_views.MemberViewSet, basename='member')

urlpatterns = router.urls
