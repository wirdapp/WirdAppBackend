from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'contest', views.ContestView, basename='contests')
router.register(r'signup', views.SignUpView, basename='signup')
# router.register(r'contest-person', views.ContestPersonView, basename='contest-persons')

urlpatterns = [
    path('', include(router.urls)),
]
