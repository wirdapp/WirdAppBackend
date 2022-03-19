from django.contrib.auth import password_validation
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from core.serializers import set_competition, CompetitionFilteredPrimaryKeyRelatedField
from student.models import StudentUser
from .models import *


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        depth = 2
        exclude = ('competition',)

    def create(self, validated_data):
        section = super(SectionSerializer, self).create(validated_data)
        return set_competition(self.context, section)


class PointTemplateSerializer(serializers.ModelSerializer):
    section = CompetitionFilteredPrimaryKeyRelatedField(clazz=Section)

    class Meta:
        model = PointTemplate
        depth = 2
        exclude = ('competition',)

    def create(self, validated_data):
        point_template = super(PointTemplateSerializer, self).create(validated_data)
        return set_competition(self.context, point_template)

    def validate_lower_units_bound(self, value):
        if self.initial_data['form_type'] == 'oth':
            return -1
        else:
            return value


class CompGroupSerializer(serializers.ModelSerializer):
    group_students = CompetitionFilteredPrimaryKeyRelatedField(clazz=StudentUser, many=True)
    admin = CompetitionFilteredPrimaryKeyRelatedField(clazz=CompAdmin)

    class Meta:
        model = CompGroup
        depth = 2
        exclude = ('competition',)

    def create(self, validated_data):
        admin = self.context['request'].user.competition_admins
        comp_group = super(CompGroupSerializer, self).create(validated_data)
        comp_group.set_admin(admin)
        return set_competition(self.context, comp_group)


class CompAdminSerializer(serializers.ModelSerializer):
    managed_groups = CompetitionFilteredPrimaryKeyRelatedField(clazz=CompGroup, many=True, read_only=True)

    def validate_password(self, value):
        password_validation.validate_password(value, self.instance)
        return make_password(value)

    class Meta:
        model = CompAdmin
        depth = 2
        fields = ['password', 'username', 'email', 'phone_number', 'first_name', 'last_name', 'managed_groups',
                  'permissions', 'is_super_admin']

        extra_kwargs = {'password': {'write_only': True}, }

    def create(self, validated_data):
        comp_admin = super(CompAdminSerializer, self).create(validated_data)
        if self.check_admin_added(self.context, comp_admin):
            return comp_admin
        return set_competition(self.context, comp_admin)

    def check_admin_added(self, context, comp_admin):
        if context['request'].user.is_staff:
            comp_id = context['request'].query_params.get('c')
            if not comp_id:
                comp_admin.delete()
                raise Exception("You forgot smthng ;)")
            comp_admin.set_competition(Competition.objects.get(id=comp_id))
            comp_admin.save()
            return True


class CompAdminRetrieveUpdateSerializer(CompAdminSerializer):
    managed_groups = CompetitionFilteredPrimaryKeyRelatedField(clazz=CompGroup, serializer=CompGroupSerializer,
                                                               many=True, read_only=True)

    class Meta:
        model = CompAdmin
        depth = 1
        fields = ['username', 'email', 'phone_number', 'first_name', 'last_name', 'managed_groups', 'permissions',
                  'is_super_admin']
        extra_kwargs = {'username': {'read_only': True}, }


class CompAdminChangePasswordSerializer(serializers.ModelSerializer):
    def validate_password(self, value):
        password_validation.validate_password(value, self.instance)
        return make_password(value)

    class Meta:
        model = CompAdmin
        depth = 2
        fields = ['username', 'password']

        extra_kwargs = {'username': {'read_only': True}, }


class AdminCompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        depth = 1
        fields = '__all__'
        extra_kwargs = {'id': {'read_only': True}, }
