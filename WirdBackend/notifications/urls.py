from django.urls import path, include
from rest_framework.routers import DefaultRouter
from notifications.views import UserDeviceViewSet, AllNotificationViewSet

router = DefaultRouter()
router.register("devices", UserDeviceViewSet, basename="device")
urlpatterns = [
    path('', include(router.urls)),
    path("<str:contest_id>/all/",AllNotificationViewSet.as_view(),name="all-notifications",),
]
