from django.contrib.auth import password_validation
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from core.serializers import set_competition, CompetitionFilteredPrimaryKeyRelatedField
from student.models import StudentUser
from student.serializers import PointRecordSerializer
from .models import *


class PointFormatSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointFormat
        depth = 2
        fields = '__all__'


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        depth = 2
        exclude = ('competition',)

    def create(self, validated_data):
        section = super(SectionSerializer, self).create(validated_data)
        return set_competition(self.context, section)


class PointTemplateSerializer(serializers.ModelSerializer):
    form_type = serializers.PrimaryKeyRelatedField(queryset=PointFormat.objects.all())
    section = CompetitionFilteredPrimaryKeyRelatedField(Section)

    class Meta:
        model = PointTemplate
        depth = 2
        exclude = ('competition',)

    def create(self, validated_data):
        point_template = super(PointTemplateSerializer, self).create(validated_data)
        return set_competition(self.context, point_template)


class CompGroupSerializer(serializers.ModelSerializer):
    extra_challenges = CompetitionFilteredPrimaryKeyRelatedField(PointTemplate, many=True)
    group_students = CompetitionFilteredPrimaryKeyRelatedField(StudentUser, many=True)

    class Meta:
        model = CompGroup
        depth = 2
        exclude = ('competition', 'admin',)

    def create(self, validated_data):
        admin = self.context['request'].user.competition_admins
        comp_group = super(CompGroupSerializer, self).create(validated_data)
        comp_group.set_admin(admin)
        return set_competition(self.context, comp_group)


class CompAdminSerializer(serializers.ModelSerializer):
    managed_groups = CompetitionFilteredPrimaryKeyRelatedField(CompGroup, many=True)

    def validate_password(self, value):
        password_validation.validate_password(value, self.instance)
        return make_password(value)

    class Meta:
        model = CompAdmin
        depth = 2
        fields = ['password', 'username', 'first_name', 'last_name', 'managed_groups',
                  'permissions', 'is_super_admin']

        extra_kwargs = {'password': {'write_only': True}, }

    def create(self, validated_data):
        comp_admin = super(CompAdminSerializer, self).create(validated_data)
        return set_competition(self.context, comp_admin)


class CompAdminRetrieveUpdateSerializer(CompAdminSerializer):
    managed_groups = CompetitionFilteredPrimaryKeyRelatedField(CompGroup, many=True)

    class Meta:
        model = CompAdmin
        depth = 1
        fields = ['username', 'managed_groups', 'first_name', 'last_name']
        extra_kwargs = {'username': {'read_only': True}, }


class CompAdminChangePasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompAdmin
        depth = 2
        fields = ['username', 'password']

        extra_kwargs = {'username': {'read_only': True}, }


class StudentUserSerializer(serializers.ModelSerializer):
    student_points = serializers.SerializerMethodField()

    def get_student_points(self, obj):
        # TODO: Make it the current day of ramadan instead of 1
        ramadan_date = self.context['request'].query_params.get('ramadan_date', 1)
        points = obj.student_points.filter(ramadan_record_date=ramadan_date)
        return PointRecordSerializer(points, many=True).data

    class Meta:
        model = StudentUser
        depth = 1
        fields = ['username', 'first_name', 'last_name', 'total_points', 'read_only', 'profile_photo', 'student_points',
                  'total_points']

        extra_kwargs = {
            'username': {'read_only': True},
            'total_points': {'read_only': True},
        }


class StudentChangePasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentUser
        depth = 1
        fields = ['username', 'password']

        extra_kwargs = {'username': {'read_only': True}, }
