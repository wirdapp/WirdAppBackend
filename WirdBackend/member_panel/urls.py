import datetime

from django.shortcuts import redirect
from django.urls import path, include
from rest_framework import routers

from . import views

urlpatterns = [
    path('point-records/', lambda request: redirect('/member-panel/point-records/' + datetime.date.today().isoformat())),
    path('point-records/<date:date>/', views.ResultsByDateView.as_view(), name='Point Templates Page'),
    path('point-templates/', lambda request: redirect('/member-panel/point-templates/' + datetime.date.today().isoformat())),
    path('point-templates/<date:date>/', views.ReadOnlyPointTemplateView.as_view({'get': 'list'}), name='Point Templates Page'),

]
