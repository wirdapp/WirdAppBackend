from django.contrib import admin

from notifications.models import UserDevice, Notification, NotificationLog

admin.site.register(UserDevice)
admin.site.register(Notification)


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    readonly_fields = ('sent_at',)
