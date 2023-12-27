from django.urls import include
from django.urls import path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()

router.register(r'criteria', views.ContestCriterionView, basename='ContestCriterionView')
router.register(r'section', views.SectionView, basename='Section')
router.register(r'groups', views.GroupView, basename='Groups')
router.register(r'person_groups', views.ContestPersonGroupView, basename='PersonGroups')
router.register(r'contest_people', views.ContestPersonView, basename='Contest People')
urlpatterns = [
    path('', include(router.urls)),
]
