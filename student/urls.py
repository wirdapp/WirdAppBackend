from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'student-user', views.StudentUserView, basename='StudentUser')
router.register(r'point-records', views.PointRecordsView, basename='PointRecord')
router.register(r'point-templates', views.PointTemplatesView, basename='StudentPointTemplate')
router.register(r'announcements', views.AnnouncementsView, basename='Announcements')

urlpatterns = [
    path('', include(router.urls)),
    path('admin-info/', views.GroupAdminInformationView.as_view(), name='Group Admin Info'),
]
