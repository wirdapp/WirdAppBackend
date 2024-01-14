from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'contests', views.ContestView, basename='contests')

urlpatterns = [
    path('current_user/', views.CurrentUserView.as_view()),
    path('', include(router.urls)),
]
