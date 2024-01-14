from django.urls import include
from django.urls import path
from . import views
from rest_framework_nested import routers

router = routers.DefaultRouter()

router.register(r'criteria', views.ContestCriterionView, basename='ContestCriterionView')
router.register(r'section', views.SectionView, basename='Section')
router.register(r'contest_members', views.ContestMembersView, basename='Contest Members')

router.register(r'groups', views.GroupView, basename='groups')
groups_router = routers.NestedSimpleRouter(router, r'groups', lookup='group')
groups_router.register(r'members', views.ContestPersonGroupView, basename='group_members')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(groups_router.urls)),
]
