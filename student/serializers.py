from collections import OrderedDict

from django.contrib.auth import password_validation
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from compAdmin.models import Competition
from core.serializers import CompetitionFilteredPrimaryKeyRelatedField
from .models import *


class ReadOnlyPointTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointTemplate
        depth = 2
        fields = ['id', 'label', "description", "form_type", "upper_units_bound", "lower_units_bound",
                  "points_per_unit"]


class PointRecordSerializer(serializers.ModelSerializer):
    point_template = CompetitionFilteredPrimaryKeyRelatedField(clazz=PointTemplate, serializer=ReadOnlyPointTemplateSerializer)
    student = serializers.CharField(read_only=True, source='student.username')

    class Meta:
        model = PointRecord
        depth = 0
        fields = '__all__'
        extra_kwargs = {'point_total': {'read_only': True}}

    def validate(self, attrs):
        errors = OrderedDict()
        point_template = attrs['point_template']
        scored_units = attrs['point_scored_units']
        record_date = attrs['ramadan_record_date']
        user = self.context['request'].user
        competition = user.competition
        if hasattr(user, 'competition_students'):
            student = user.competition_students     # user scoring for themselves
        else:
            student = self.initial_data['student']  # admin editing for a student
        not_exists = not student.student_points.filter(ramadan_record_date=record_date, point_template=point_template).exists()
        is_update = self.context['request'].method == 'PUT'
        self.check(not_exists or is_update, 'You can\'t score the same point again', errors)
        self.check(not (student.read_only or competition.readonly_mode), 'You can\'t score new points', errors)
        self.check(point_template.is_active and point_template.is_shown, 'Point is not active', errors)
        if not (point_template.form_type == 'oth' and scored_units == -1):
            self.check(point_template.upper_units_bound >= scored_units >= point_template.lower_units_bound
                       , 'Point is beyond limits', errors)
        self.check(30 >= record_date >= 1, 'Date is beyond limits', errors)
        self.check(30 >= record_date >= 1, 'Date is beyond limits', errors)
        if point_template.custom_days:
            self.check(str(record_date) in point_template.custom_days.split(','), 'Point is not active on this day', errors)
        if len(errors) > 0:
            raise ValidationError(errors)
        return attrs

    def check(self, statement, message, errors):
        if not statement:
            errors['Error'] = message

    def create(self, validated_data):
        student_user = self.context['request'].user.competition_students
        point = super(PointRecordSerializer, self).create(validated_data)
        point.set_student(student_user)
        point.set_point_total(self.get_point_total(validated_data))
        point.save()
        return point

    def update(self, instance, validated_data):
        instance.set_point_total(self.get_point_total(validated_data))
        return super(PointRecordSerializer, self).update(instance, validated_data)

    @classmethod
    def get_point_total(cls, validated_data):
        units = validated_data['point_scored_units']
        ppu = validated_data['point_template'].points_per_unit
        return units * ppu


class StudentUserSerializer(serializers.ModelSerializer):
    competition = serializers.PrimaryKeyRelatedField(queryset=Competition.objects.all())

    def validate_password(self, value):
        password_validation.validate_password(value, self.instance)
        return make_password(value)

    class Meta:
        model = StudentUser
        depth = 2
        fields = ['username', 'password', 'first_name', 'last_name', 'profile_photo', 'total_points', 'competition']

        extra_kwargs = {'password': {'write_only': True},
                        'competition': {'write_only': True},
                        'total_points': {'read_only': True},
                        }


class StudentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentUser
        depth = 1
        fields = ['username', 'first_name', 'last_name', 'profile_photo', 'total_points']
        extra_kwargs = {'username': {'read_only': True}, 'total_points': {'read_only': True}, }
