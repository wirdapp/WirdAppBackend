from django.urls import path, include
from rest_framework import routers

from . import views
from . import student_views

router = routers.DefaultRouter()
router.register(r'comp-admins', views.CompAdminView, basename='CompAdmin')
router.register(r'comp-group', views.CompGroupView, basename='CompGroup')
router.register(r'point-template', views.PointTemplatesView, basename='PointTemplate')
router.register(r'section', views.SectionView, basename='Section')
router.register(r'comp-view', views.AdminCompetitionView, basename='AdminCompetitionView')
router.register(r'students', student_views.StudentView, basename='Students')

urlpatterns = [
    path('', include(router.urls)),
    path('admin-info/', views.AdminInformationView.as_view(), name='Admin info'),
    path('export-comp-info/', views.ExportInformation.as_view(), name='Export Competition Info'),
]
