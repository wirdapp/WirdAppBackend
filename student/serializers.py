from django.contrib.auth import password_validation
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from compAdmin.models import Competition
from .models import *


class PointRecordSerializer(serializers.ModelSerializer):
    point_template = serializers.PrimaryKeyRelatedField(queryset=PointTemplate.objects.all())

    class Meta:
        model = PointRecord
        depth = 1
        fields = '__all__'

    def create(self, validated_data):
        student_user = self.context['request'].user
        if isinstance(student_user, StudentUser):
            point = super(PointRecordSerializer, self).create(validated_data)
            point.set_student(student_user)
            point.save()
            return point
        return PointRecord()

    def validate_point_total_score(self):
        pass


class StudentUserSerializer(serializers.ModelSerializer):
    competition = serializers.PrimaryKeyRelatedField(queryset=Competition.objects.all())
    student_points = PointRecordSerializer(many=True, read_only=True)

    def validate_password(self, value):
        password_validation.validate_password(value, self.instance)
        return make_password(value)

    class Meta:
        model = StudentUser
        depth = 2
        fields = ['username', 'password', 'first_name', 'last_name', 'profile_photo', 'competition',
                  'student_points']

        extra_kwargs = {'password': {'write_only': True},
                        'competition': {'write_only': True}, }


class StudentUserAdminUpdateSerializer(serializers.ModelSerializer):
    student_points = PointRecordSerializer(many=True)

    class Meta:
        model = StudentUser
        depth = 2
        fields = ['username', 'first_name', 'last_name', 'read_only', 'student_points']

        extra_kwargs = {'username': {'read_only': True}, }


class StudentUserStudentUpdateSerializer(serializers.ModelSerializer):
    student_points = PointRecordSerializer(many=True)

    class Meta:
        model = StudentUser
        depth = 2
        fields = ['username', 'first_name', 'last_name', 'profile_photo', 'student_points']
        extra_kwargs = {'username': {'read_only': True}, }
