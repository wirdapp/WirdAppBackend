from django.contrib.auth import password_validation
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from core import util
from student.models import StudentUser, PointRecord
from student.serializers import PointRecordSerializer, ReadOnlyPointTemplateSerializer


class StudentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentUser
        depth = 1
        fields = ['username', 'first_name', 'last_name', 'total_points', 'read_only', 'profile_photo']

        extra_kwargs = {
            'username': {'read_only': True},
            'total_points': {'read_only': True},
        }


class ReadOnlyPointRecordSerializer(serializers.ModelSerializer):
    point_template = ReadOnlyPointTemplateSerializer(read_only=True)

    class Meta:
        model = PointRecord
        depth = 1
        exclude = ('user_input', 'student',)


class UpdatePointRecordSerializer(PointRecordSerializer):
    class Meta:
        model = PointRecord
        depth = 1
        fields = '__all__'
        extra_kwargs = {'point_total': {'read_only': True}}


class StudentUserRetrieveSerializer(serializers.ModelSerializer):
    student_points = serializers.SerializerMethodField()

    def get_student_points(self, instance):
        date = self.context['request'].query_params.get('date', util.get_today_date_hijri())
        student_points = instance.student_points.filter(ramadan_record_date=date)
        return ReadOnlyPointRecordSerializer(student_points, many=True, read_only=True).data

    class Meta:
        model = StudentUser
        depth = 1
        fields = ['username', 'first_name', 'last_name', 'total_points', 'read_only', 'profile_photo', 'student_points',
                  'total_points']

        extra_kwargs = {
            'username': {'read_only': True},
            'total_points': {'read_only': True},
            'student_points': {'read_only': True},
        }


class StudentChangePasswordSerializer(serializers.ModelSerializer):
    def validate_password(self, value):
        password_validation.validate_password(value, self.instance)
        return make_password(value)

    class Meta:
        model = StudentUser
        depth = 1
        fields = ['username', 'password']

        extra_kwargs = {'username': {'read_only': True}, }
