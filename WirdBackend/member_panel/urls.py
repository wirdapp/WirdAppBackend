from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'point-records', views.PointRecordsView, basename='point_records')
router.register(r'point-templates', views.ReadOnlyPointTemplateView, basename='point_templates')

urlpatterns = [
    path('', include(router.urls)),
]
