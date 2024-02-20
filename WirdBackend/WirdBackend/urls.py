"""WirdBackend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from dj_rest_auth.registration.views import VerifyEmailView
from django.urls import path, include, re_path, register_converter
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from core.util_classes import DateConverter
from core.views import DeleteUserView, ResendEmailConfirmation, UsernameResetView
from dj_rest_auth.views import PasswordResetConfirmView

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
    path("auth/registration/account-confirm-email/", VerifyEmailView.as_view()),
    path('auth/user/resend_confirmation_email/', ResendEmailConfirmation.as_view(), name='resend-email-confirmation'),
    path('auth/user/delete/', DeleteUserView.as_view(), name='resend-email-confirmation'),
    path('auth/username/reset/', UsernameResetView.as_view(), name='Forgot Username Stats'),
    path('auth/password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    path('auth/', include('dj_rest_auth.urls')),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
