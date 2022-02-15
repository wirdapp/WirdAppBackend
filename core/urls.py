from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'competitions', views.CompetitionView, basename='CompAdmin')

urlpatterns = [
    path('', include(router.urls)),
]
