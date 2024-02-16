from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'contests', views.ContestView, basename='contests')

urlpatterns = [
    path('', include(router.urls)),
    path('general_stats/', views.GeneralStatsView.as_view(), name='General Stats'),
]
