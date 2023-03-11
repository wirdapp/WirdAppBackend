from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'competition', views.CompetitionView, basename='Competitions')
router.register(r'create-competition', views.CreateCompetitionView, basename='CreateCompetition')

urlpatterns = [
    path('', include(router.urls)),
    path('check_username_pwd/', views.CheckUserNamePasswordView.as_view(), name='check_username_pwd'),
]  # + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
