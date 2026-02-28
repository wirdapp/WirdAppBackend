from django.urls import path, include
from rest_framework.routers import DefaultRouter
from notifications.views import UserDeviceViewSet, AllNotificationViewSet

devices_router = DefaultRouter()
devices_router.register("devices", UserDeviceViewSet, basename="device")

notifications_router = DefaultRouter()
notifications_router.register(r"(?P<contest_id>[^/.]+)", AllNotificationViewSet, basename="all-notifications")

urlpatterns = [
    path('', include(devices_router.urls)),
    #Legacy URL
    path('<str:contest_id>/all/', AllNotificationViewSet.as_view({'get': 'list'}), name='all-notifications-legacy'),
    path('', include(notifications_router.urls)),
]
