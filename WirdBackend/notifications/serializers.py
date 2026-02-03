from rest_framework import serializers
from notifications.models import UserDevice, Notification


class UserDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDevice
        fields = '__all__'
        read_only_fields = ['user']


class AllNotificationSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.person.first_name')
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['contest', 'created_by', 'is_sent', 'sent_at']

