import datetime

from django.shortcuts import redirect
from django.urls import include
from django.urls import path, register_converter
from rest_framework import routers

from core.util_classes import DateConverter
from . import views

router = routers.DefaultRouter()

router.register(r'point-template', views.PointTemplatesView, basename='PointTemplate')
router.register(r'section', views.SectionView, basename='Section')
router.register(r'groups', views.GroupView, basename='Groups')
router.register(r'contest-people', views.ContestPersonView, basename='Contest People')
register_converter(DateConverter, 'date')

urlpatterns = [
    path('', include(router.urls)),
    path('top_members/', views.TopMembers.as_view(), name='top_members'),
    path('results/', lambda request: redirect('/admin-panel/results/' + datetime.date.today().isoformat())),
    path('results/<date:date>/', views.ResultsView.as_view(), name='Results Page'),
    path('results/<date:date>/<str:group_id>', views.GroupMemberResultsView.as_view(), name='Results Page'),
]
