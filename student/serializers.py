from django.contrib.auth import password_validation
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from compAdmin.models import Competition
from core.serializers import CompetitionFilteredPrimaryKeyRelatedField
from .models import *


class PointRecordSerializer(serializers.ModelSerializer):
    point_template = CompetitionFilteredPrimaryKeyRelatedField(PointTemplate)

    class Meta:
        model = PointRecord
        depth = 1
        exclude = ('student',)
        extra_kwargs = {'point_total': {'read_only': True}}

    def validate(self, attrs):
        user = self.context['request'].user
        point_template = attrs['point_template']
        scored_units = attrs['point_scored_units']
        record_date = attrs['ramadan_record_date']
        assert hasattr(user, 'competition_students'), 'Only student can create or update points'
        assert point_template.is_active and point_template.is_shown, 'Point is not active'
        assert point_template.upper_units_bound >= scored_units >= point_template.lower_units_bound, 'Point is beyond limits'
        assert 30 >= record_date >= 1, 'Date is beyond limits'
        assert str(record_date) in point_template.custom_days.split(','), 'Point is not active on this day'
        return attrs

    def create(self, validated_data):
        student_user = self.context['request'].user.competition_students
        point = super(PointRecordSerializer, self).create(validated_data)
        point.set_student(student_user)
        point.set_point_total(self.set_point_total(validated_data))
        point.save()
        return point

    def update(self, instance, validated_data):
        instance.set_point_total(self.set_point_total(validated_data))
        return super(PointRecordSerializer, self).update(instance, validated_data)

    @classmethod
    def set_point_total(cls, validated_data):
        units = validated_data['point_scored_units']
        ppu = validated_data['point_template'].points_per_unit
        return units * ppu


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
    student_points = PointRecordSerializer(many=True, read_only=True)

    class Meta:
        model = StudentUser
        depth = 2
        fields = ['username', 'first_name', 'last_name', 'read_only', 'profile_photo', 'student_points']

        extra_kwargs = {'username': {'read_only': True}, }


class StudentUserStudentUpdateSerializer(serializers.ModelSerializer):
    student_points = PointRecordSerializer(many=True, read_only=True)

    class Meta:
        model = StudentUser
        depth = 2
        fields = ['username', 'first_name', 'last_name', 'profile_photo', 'student_points']
        extra_kwargs = {'username': {'read_only': True}, }
