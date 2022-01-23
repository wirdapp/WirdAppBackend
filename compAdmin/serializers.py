from django.contrib.auth import password_validation
from rest_framework import serializers

from django.contrib.auth.hashers import make_password

from core.serializers import set_competition, CompetitionFilteredPrimaryKeyRelatedField
from student.models import StudentUser
from .models import *


class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        depth = 1
        fields = '__all__'


class PointTemplateSerializer(serializers.ModelSerializer):
    form_type = serializers.PrimaryKeyRelatedField(queryset=PointFormat.objects.all())

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
        fields = ['id', 'name', 'announcements', 'extra_challenges', 'group_students']

    def create(self, validated_data):
        comp_group = super(CompGroupSerializer, self).create(validated_data)
        return set_competition(self.context, comp_group)


class CompAdminSerializer(serializers.ModelSerializer):
    managed_groups = CompetitionFilteredPrimaryKeyRelatedField(CompGroup, many=True)

    def validate_password(self, value):
        password_validation.validate_password(value, self.instance)
        return make_password(value)

    class Meta:
        model = CompAdmin
        depth = 2
        fields = ['username', 'password', 'first_name', 'last_name', 'managed_groups',
                  'permissions', 'is_super_admin']

        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        comp_admin = super(CompAdminSerializer, self).create(validated_data)
        return set_competition(self.context, comp_admin)


class CompAdminRetrieveUpdateSerializer(CompAdminSerializer):
    class Meta:
        model = CompAdmin
        depth = 1
        fields = ['first_name', 'last_name', 'managed_groups', 'permissions', 'is_super_admin']
