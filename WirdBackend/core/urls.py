from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'contest', views.ContestView, basename='contests')
router.register(r'signup', views.SignUpView, basename='signup')

urlpatterns = [
    path('current-user/', views.CurrentContestPersonView.as_view({'get': 'retrieve', "post": "update"}),
         name='current-persons'),
    path("top-members/", views.TopMembersOverall.as_view()),
    path("top-members/<date:date>", views.TopMembersByDate.as_view()),
    path('', include(router.urls)),
]
