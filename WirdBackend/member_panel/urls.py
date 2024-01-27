from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'point_records/(?P<date>\d{4}-\d{2}-\d{2})', views.MemberPointRecordViewSet, basename='PointRecords')
router.register(r'contest_criteria', views.ContestCriteriaViewSet, basename='Criteria')
router.register(r'sections', views.ContestSectionsViewSet, basename='Sections')

urlpatterns = [
    path('', include(router.urls)),
    path('results/', views.UserResultsView.as_view(), name=''),
    path('leaderboard/', views.Leaderboard.as_view(), name=''),
    path('home/', views.HomePageView.as_view(), name=''),
]
