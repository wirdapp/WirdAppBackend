from django.contrib import admin

from notifications.models import UserDevice, Notification, NotificationLog
from notifications.tasks import send_admin_notification_task


@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ['user', 'device_type', 'created_at', 'updated_at']
    list_filter = ['device_type', 'created_at']
    search_fields = ['user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Notification)
class AdminNotificationAdmin(admin.ModelAdmin):
    list_display = [
        'contest', 'is_sent', 'sent_at', 'created_by'
    ]
    list_filter = ['is_sent', 'contest']
    search_fields = ['title', 'body']
    readonly_fields = ['is_sent', 'sent_at', 'created_by']
    actions = ['send_notification']

    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    @admin.action(description='Send selected notifications')
    def send_notification(self, request, queryset):
        for notification in queryset.filter(is_sent=False):
            send_admin_notification_task.delay(notification.id)
        self.message_user(request, f"Queued {queryset.count()} notifications for sending")


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ['notification_type', 'success']
    list_filter = ['notification_type', 'success']
    readonly_fields = ['notification_type', 'success', 'error_message']
