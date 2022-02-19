from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'student-user', views.StudentUserView, basename='StudentUser')
router.register(r'point-records', views.PointRecordsView, basename='PointRecord')
router.register(r'point-templates', views.PointTemplatesView, basename='StudentPointTemplate')
router.register(r'advertisements', views.AdvertisementsView, basename='Advertisements')

urlpatterns = [
    path('', include(router.urls)),
]
