from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()

router.register(r'point-template', views.PointTemplatesView, basename='PointTemplate')
router.register(r'section', views.SectionView, basename='Section')
router.register(r'groups', views.GroupView, basename='Groups')


urlpatterns = [
    path('', include(router.urls)),
]
