from django.urls import path, include
from rest_framework.routers import DefaultRouter
from notifications.views import UserDeviceViewSet, AllNotificationViewSet

router = DefaultRouter()
router.register("devices", UserDeviceViewSet, basename="device")
router.register("all", AllNotificationViewSet, basename="all")
urlpatterns = [
    path('', include(router.urls)),
]
