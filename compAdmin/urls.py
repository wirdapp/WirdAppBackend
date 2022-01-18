from django.urls import path
from . import views

urlpatterns = [
    path('points-template/', views.PointTemplates.as_view()),
    path('comp-group/', views.CompGroupTemplate.as_view()),
]
