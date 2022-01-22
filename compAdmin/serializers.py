from django.contrib.auth import password_validation
from rest_framework import serializers

from core.serializers import create_general_user, set_competition, CompetitionQuerySet, check_if_field_valid
from django.contrib.auth.hashers import make_password

from student.models import StudentUser
from student.serializers import StudentUserSerializer
from .models import *


class CompetitionFilteredPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def __init__(self, clazz, **kwargs):
        self.clazz = clazz
        super(CompetitionFilteredPrimaryKeyRelatedField, self).__init__(**kwargs)

    def get_queryset(self):
        competition = self.context['request'].user.competition
        return self.clazz.objects.filter(competition=competition)

    def to_internal_value(self, data):
        return self.get_queryset().get(pk=data)


class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        depth = 1
        fields = 'id'


class PointTemplateSerializer(serializers.ModelSerializer):
    form_type = serializers.PrimaryKeyRelatedField(queryset=PointFormat.objects.all())

    class Meta:
        model = PointTemplate
        depth = 2
        exclude = ('competition',)

    def create(self, validated_data):
        point_template = super(PointTemplateSerializer, self).create(validated_data)
        point_template.set_competition(self.context['request'].user.competition)
        return point_template


class CompGroupSerializer(serializers.ModelSerializer):
    extra_challenges = CompetitionFilteredPrimaryKeyRelatedField(PointTemplate, many=True)
    students = CompetitionFilteredPrimaryKeyRelatedField(StudentUser, many=True)

    class Meta:
        model = CompGroup
        depth = 2
        fields = ['id', 'name', 'announcements', 'extra_challenges', 'students']

    def create(self, validated_data):
        comp_group = super(CompGroupSerializer, self).create(validated_data)
        comp_group.set_competition(self.context['request'].user.competition)
        return comp_group


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
        comp_admin.set_competition(self.context['request'].user.competition)
        return comp_admin


class CompAdminRetrieveUpdateSerializer(CompAdminSerializer):
    class Meta:
        model = CompAdmin
        depth = 1
        fields = ['first_name', 'last_name', 'managed_groups', 'permissions', 'is_super_admin']
