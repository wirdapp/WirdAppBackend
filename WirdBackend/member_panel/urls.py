from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'point_records/(?P<date>\d{4}-\d{2}-\d{2})', views.MemberPointRecordViewSet, basename='PointRecords')
router.register(r'contest_criteria/(?P<date>\d{4}-\d{2}-\d{2})', views.ContestCriteriaViewSet, basename='Criteria')
router.register(r'sections', views.ContestSectionsViewSet, basename='Sections')

urlpatterns = [
    path('', include(router.urls))
]
