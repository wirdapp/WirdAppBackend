from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'student-user', views.StudentUserView, basename='StudentUser')
router.register(r'record-point', views.PointRecordsView, basename='PointRecord')

urlpatterns = [
    path('', include(router.urls)),
]
