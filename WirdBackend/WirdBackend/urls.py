from django.conf import settings
from django.urls import path, include, register_converter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.contrib import admin
from core.util_classes import DateConverter

register_converter(DateConverter, 'date')

schema_view = get_schema_view(
    openapi.Info(
        title="Wird APIs",
        default_version='v1',
        description="Wird endpoints documentation",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="help@wird.app"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('', include('core.urls')),
    path('admin_panel/<str:contest_id>/', include('admin_panel.urls')),
    path('member_panel/<str:contest_id>/', include('member_panel.urls')),
    path('auth/', include('auth_kit.urls')),
    path('local-auth/', include('rest_framework.urls')),
]

# Add API documentation if enabled
if getattr(settings, 'ENABLE_API_DOCS', False):
    urlpatterns += [
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ]

# Add DRF auth endpoints only if GUI is enabled
if getattr(settings, 'ENABLE_GUI', False):
    urlpatterns.append(path('local-auth/', include('rest_framework.urls')))

if getattr(settings, 'ENABLE_ADMIN', False):
    urlpatterns.append(path('admin/', admin.site.urls))