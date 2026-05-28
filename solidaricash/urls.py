from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('apps.authentication.urls', namespace='auth')),
    path('dashboard/', include('apps.members.urls', namespace='members')),
    path('cycles/', include('apps.cycles.urls', namespace='cycles')),
    path('contributions/', include('apps.contributions.urls', namespace='contributions')),
    path('rotation/', include('apps.rotation.urls', namespace='rotation')),
    path('distributions/', include('apps.distributions.urls', namespace='distributions')),
    path('emergencies/', include('apps.emergencies.urls', namespace='emergencies')),
    path('notifications/', include('apps.notifications.urls', namespace='notifications')),
    path('reports/', include('apps.reports.urls', namespace='reports')),
    path('audit/', include('apps.audit.urls', namespace='audit')),
    path('', include('apps.authentication.urls_home')),
    # DRF API
    path('api/auth/', include('apps.authentication.api_urls')),
    path('api/members/', include('apps.members.api_urls')),
    path('api/cycles/', include('apps.cycles.api_urls')),
    path('api/contributions/', include('apps.contributions.api_urls')),
    path('api/rotation/', include('apps.rotation.api_urls')),
    path('api/distributions/', include('apps.distributions.api_urls')),
    path('api/emergencies/', include('apps.emergencies.api_urls')),
    path('api/notifications/', include('apps.notifications.api_urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
