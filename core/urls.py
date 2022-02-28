from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'competition', views.CompetitionView, basename='Competitions')
router.register(r'create-competition', views.CreateCompetitionView, basename='CreateCompetition')

urlpatterns = [
    path('', include(router.urls)),
]
