from rest_framework import serializers
from .models import *


class PointRecordSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = PointRecord
        depth = 1
        fields = '__all__'


class StudentUserSerializer(serializers.ModelSerializer):
    competition = serializers.CharField(source='competition.id', read_only=True)
    group = serializers.CharField(source='group.id', read_only=True)

    class Meta:
        model = StudentUser
        depth = 1
        fields = ['username', 'password', 'first_name', 'last_name', 'total_points', 'read_only', 'competition',
                  'group']
        extra_kwargs = {'password': {'write_only': True}, 'total_points': {'read_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = StudentUser(**validated_data)
        user.set_password(password)
        user.save()
        return user
