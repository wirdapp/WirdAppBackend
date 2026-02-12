import uuid

from django.db import models


class UserDevice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'core.Person',
        on_delete=models.CASCADE,
        related_name='devices'
    )
    fcm_token = models.CharField(max_length=500, unique=True)
    device_type = models.CharField(
        max_length=10,
        choices=[('ios', 'iOS'), ('android', 'Android')],
        default='android'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.device_type}"


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contest = models.ForeignKey(
        'core.Contest',
        on_delete=models.CASCADE,
        related_name='admin_notifications'
    )
    created_by = models.ForeignKey(
        'core.ContestPerson',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_notifications'
    )
    title = models.CharField(max_length=200)
    body = models.TextField(max_length=1500)
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.contest} - {self.title[:50]}"


class NotificationLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification_type = models.CharField(
        max_length=50,
        choices=[
            ('daily_reminder', 'Daily Reminder'),
            ('admin_notification', 'Admin Notification'),
        ]
    )
    receiver = models.ForeignKey(
        'core.ContestPerson',
        on_delete=models.CASCADE,
        null=True
    )
    error_message = models.TextField(null=True, blank=True)
    success = models.BooleanField(default=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.notification_type} - {self.receiver} - {self.sent_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-sent_at']
