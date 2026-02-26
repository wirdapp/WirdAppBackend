from django_q.tasks import async_task
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.permissions import IsContestMember, IsContestSuperAdmin
from core.util_methods import get_current_contest_person, get_current_contest
from notifications.models import Notification, UserDevice
from notifications.serializers import UserDeviceSerializer, AllNotificationSerializer
from core.util_classes import CustomPermissionsMixin

class UserDeviceViewSet(ModelViewSet):
    serializer_class = UserDeviceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserDevice.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        token = request.data.get('fcm_token')
        device, created = UserDevice.objects.get_or_create(
            fcm_token=token,
            defaults={'user': request.user}
        )
        if not created and device.user != request.user:
            # Token switched to a new user — reassign it
            device.user = request.user
            device.save(update_fields=['user'])
        serializer = self.get_serializer(device)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(serializer.data, status=status_code)


class AllNotificationViewSet(CustomPermissionsMixin, ModelViewSet):
    serializer_class = AllNotificationSerializer
    member_allowed_methods = ["list"]
    super_admin_allowed_methods = ["create", "destroy", "partial_update", "update", "retrieve"]

    def get_queryset(self):
        contest = get_current_contest(self.request)
        return Notification.objects.filter(contest=contest)

    def perform_create(self, serializer):
        contest_person = get_current_contest_person(self.request)
        notification = serializer.save(created_by=contest_person, contest=contest_person.contest)
        async_task("notifications.tasks.send_admin_notification_task", notification)
