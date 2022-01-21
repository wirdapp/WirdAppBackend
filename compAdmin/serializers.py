from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from core.serializers import create_general_user, set_competition, CompetitionQuerySet
from student.models import StudentUser
from student.serializers import StudentUserSerializer
from .models import *


class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        depth = 1
        fields = 'id'


class PointTemplateSerializer(serializers.ModelSerializer):
    form_type = serializers.RelatedField(queryset=PointFormat.objects.all())

    class Meta:
        model = PointTemplate
        depth = 2
        fields = '__all__'

    def create(self, validated_data):
        return set_competition(self.context.user.competition, validated_data, PointTemplate)


class CompGroupSerializer(serializers.ModelSerializer):
    # def get_extra_challenges(self, obj):
    #     return PointTemplateSerializer(
    #         PointTemplate.objects.filter(competition=self.context['request'].user.competition),
    #         many=True).data

    # extra_challenges = SerializerMethodField()

    extra_challenges = PointTemplateSerializer(many=True)
    students = StudentUserSerializer(many=True)

    class Meta:
        model = CompGroup
        depth = 2
        fields = ['name', 'announcements', 'extra_challenges', 'students']

    def create(self, validated_data):
        return set_competition(self.context.user.competition, validated_data, CompGroup)


class CompAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompAdmin
        depth = 2
        fields = ['username', 'password', 'first_name', 'last_name', 'managed_groups', 'permissions',
                  'is_super_admin']

        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return create_general_user(self.context.user.competition, validated_data, CompAdmin)
