from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'point_records', views.PointRecordsView, basename='point_records')

urlpatterns = [
    path('', include(router.urls)),
]
