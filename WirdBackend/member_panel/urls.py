from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'point_records', views.MemberPointRecordViewSet, basename='PointRecords')
router.register(r'contest_criteria', views.ContestCriteriaViewSet, basename='Criteria')
router.register(r'sections', views.ContestSectionsViewSet, basename='Sections')

urlpatterns = [
    path('', include(router.urls))
]
