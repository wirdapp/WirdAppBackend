from django.contrib.auth import password_validation
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AnonymousUser
from rest_framework import serializers

from compAdmin.models import Competition
from .models import *


class PointRecordSerializer(serializers.ModelSerializer):
    point_template = serializers.PrimaryKeyRelatedField(queryset=PointTemplate.objects.all())

    class Meta:
        model = PointRecord
        depth = 1
        exclude = ('student',)

    def create(self, validated_data):
        user = self.context['request'].user
        if not isinstance(user, AnonymousUser) and user.competition_students:
            student_user = user.competition_students
            point = super(PointRecordSerializer, self).create(validated_data)
            point.set_student(student_user)
            point.save()
            return point
        else:
            return PointRecord()

    def validate_point_scored_units(self, value):
        return value


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
