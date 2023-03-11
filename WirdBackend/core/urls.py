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
    path("calendar/", views.CalendarView.as_view()),
    path("create-contest/", views.CreateNewContest.as_view()),
    path("join-contest/", views.JoinContest.as_view()),
    path("reset-password/<str:validate_get_reset>", views.ResetPasswordView.as_view()),
    path('', include(router.urls)),
]
