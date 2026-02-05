from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'contests', views.ContestView, basename='contests')

urlpatterns = [
    path('', include(router.urls)),
    path('general_stats/', views.GeneralStatsView.as_view(), name='General Stats'),
    path('health/', views.HealthCheckView.as_view(), name='health-check'),
    path("auth/username/reset/", views.UsernameResetView.as_view(), name="reset-username")
]
