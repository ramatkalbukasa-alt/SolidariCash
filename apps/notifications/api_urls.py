from django.urls import path
from rest_framework.routers import SimpleRouter
from . import api_views

router = SimpleRouter()
router.register(r'', api_views.NotificationViewSet, basename='notification')
urlpatterns = router.urls
