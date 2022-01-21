from django.urls import path
from . import views

urlpatterns = [
    path('points-template/', views.PointTemplates.as_view()),
    path('comp-group/', views.CompGroupView.as_view()),
    path('comp-admins/', views.CompAdminView.as_view()),
]
