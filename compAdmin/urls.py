from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'comp-admins', views.CompAdminView, basename='CompAdmin')
router.register(r'comp-group', views.CompGroupView, basename='CompGroup')
router.register(r'point-template', views.PointTemplatesView, basename='PointTemplate')
router.register(r'point-form', views.PointFormatView, basename='PointForm')
router.register(r'section', views.SectionView, basename='Section')

urlpatterns = [
    path('', include(router.urls)),
]
