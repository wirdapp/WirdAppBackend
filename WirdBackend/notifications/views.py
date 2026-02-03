from django_q.tasks import async_task
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from core.util_classes import CustomPermissionsMixin
from core.util_methods import get_current_contest_person, get_current_contest
from notifications.models import Notification, UserDevice
from notifications.serializers import UserDeviceSerializer, AllNotificationSerializer


class UserDeviceViewSet(ModelViewSet):
    serializer_class = UserDeviceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserDevice.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AllNotificationViewSet(CustomPermissionsMixin, ModelViewSet):
    serializer_class = AllNotificationSerializer
    member_allowed_methods = ['list']
    super_admin_allowed_methods = ["create", 'retrieve', "update", "partial_update", "destroy"]


    def get_queryset(self):
        # Filter to competitions where user is admin
        contest = get_current_contest(self.request)

        return Notification.objects.filter(
            contest=contest
        )

    def perform_create(self, serializer):
        contest_person = get_current_contest_person(self.request)
        notification = serializer.save(created_by=contest_person, contest=contest_person.contest)
        async_task("notifications.tasks.send_admin_notification_task", notification)
