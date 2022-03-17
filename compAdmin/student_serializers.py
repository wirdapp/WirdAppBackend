from django.contrib.auth import password_validation
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from compAdmin.models import PointTemplate
from core.util import current_hijri_day
from student.models import StudentUser, PointRecord


class StudentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentUser
        depth = 1
        fields = ['username', 'first_name', 'last_name', 'total_points', 'read_only', 'profile_photo']

        extra_kwargs = {
            'username': {'read_only': True},
            'total_points': {'read_only': True},
        }


class ReadOnlyPointTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointTemplate
        depth = 2
        fields = ['id', 'label', "description", "form_type", "upper_units_bound", "lower_units_bound",
                  "points_per_unit"]


class ReadOnlyPointRecordSerializer(serializers.ModelSerializer):
    point_template = ReadOnlyPointTemplateSerializer(read_only=True)
    student = serializers.CharField(read_only=True, source='student.username')

    class Meta:
        model = PointRecord
        depth = 1
        fields = "__all__"


class StudentUserRetrieveSerializer(serializers.ModelSerializer):
    student_points = serializers.SerializerMethodField()

    def get_student_points(self, instance):
        date = self.context['request'].query_params.get('date', current_hijri_day)
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
