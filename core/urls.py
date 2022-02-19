from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'competition', views.CompetitionView, basename='Competitions')

urlpatterns = [
    path('', include(router.urls)),
]
