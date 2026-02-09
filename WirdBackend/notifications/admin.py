from django.contrib import admin

from notifications.models import UserDevice, Notification, NotificationLog

from django_q.models import Schedule

admin.site.register(Schedule)
admin.site.register(UserDevice)
admin.site.register(Notification)
admin.site.register(NotificationLog)
