from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'contests', views.ContestView, basename='contests')

urlpatterns = [
    path('current_user/', views.CurrentUserView.as_view()),
    path("top-members/", views.TopMembersOverall.as_view()),
    path("top-members/<date:date>", views.TopMembersByDate.as_view()),
    path("calendar/", views.CalendarView.as_view()),
    path("calendar/<str:date>/", views.CalendarView.as_view()),
    path('', include(router.urls)),
]
