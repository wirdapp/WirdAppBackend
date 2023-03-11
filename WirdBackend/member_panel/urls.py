import datetime

from django.shortcuts import redirect
from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'point-templates', views.ReadOnlyPointTemplateView, basename='point_templates')

urlpatterns = [
    path('', include(router.urls)),
    path('point-records/', lambda request: redirect('/member-panel/point-records/' + datetime.date.today().isoformat())),
    path('point-records/<date:date>/', views.ResultsByDateView.as_view(), name='Point Records Page'),
]
