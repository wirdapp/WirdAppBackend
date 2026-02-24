from django.urls import include
from django.urls import path
from . import views, member_views
from rest_framework_nested import routers

router = routers.DefaultRouter()

router.register(r'criteria', views.ContestCriterionView, basename='ContestCriterionView')
router.register(r'sections', views.SectionView, basename='Section')
router.register(r'members', views.ContestMembersView, basename='Contest Members')
router.register(r'point_records/(?P<user_id>[0-9a-f-]+)/(?P<date>\d{4}-\d{2}-\d{2})',
                member_views.MemberPointRecordViewSet, basename='Members Point Records')
router.register(r'groups', views.GroupView, basename='groups')
groups_router = routers.NestedSimpleRouter(router, r'groups', lookup='group')
groups_router.register(r'members', views.ContestPersonGroupView, basename='group_members')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(groups_router.urls)),
    path('edit_contest/', views.ContestView.as_view()),
    path('leaderboard/', member_views.Leaderboard.as_view(), name='leaderboard'),
    path(r'results/', member_views.ContestOverallResultsView.as_view(), name='ContestResultsView'),
    path(r'results/<str:user_id>', member_views.UserResultsView.as_view(), name='ContestResultsView'),
    path('export/results/', member_views.ExportResultsView.as_view(), name='export-results'),
]
