import datetime

from django.utils.translation import gettext
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from admin_panel.models import PointTemplate
from core import util_methods
from core.models import ContestPerson
from core.util_classes import ContestFilteredPrimaryKeyRelatedField
from member_panel.models import PointRecord, UserInputPointRecord


class PointRecordSerializer(serializers.ModelSerializer):
    point_template = ContestFilteredPrimaryKeyRelatedField(helper_function_name="get_contest_point_templates",
                                                           to_repr_field="label",
                                                           to_repr_class=PointTemplate)
    record_type = serializers.ChoiceField(choices=["UserInputPointRecord", "PointRecord"], required=False)
    record_date = serializers.HiddenField(default=datetime.date.today())

    class Meta:
        exclude = ["person", "polymorphic_ctype"]
        read_only_fields = ["point_total"]
        model = PointRecord

    def to_representation(self, obj):
        if isinstance(obj, UserInputPointRecord):
            return UserInputPointRecordSerializer(obj, context=self.context).to_representation(obj)
        return super(PointRecordSerializer, self).to_representation(obj)

    def to_internal_value(self, data):
        data = data.copy()
        record_type = data.pop("record_type")
        if record_type == "UserInputPointRecord":
            self.Meta.model = UserInputPointRecord
            return UserInputPointRecordSerializer(context=self.context).to_internal_value(data)
        return super(PointRecordSerializer, self).to_internal_value(data)

    def validate(self, attrs):
        point_template = attrs["point_template"]
        attrs['record_date'] = self.context["record_date"]
        errors = dict()
        if point_template.template_type == "NumberPointTemplate":
            self.validate_number_point_template(attrs, point_template, errors)
        elif point_template.template_type == "CheckboxPointTemplate":
            self.validate_checkbox_point_template(attrs, errors)

        if point_template.custom_days:
            record_date = attrs['record_date']
            self.check_condition(record_date in point_template.custom_days, errors, "point not active day")
        self.check_condition(point_template.is_active, errors, "point not active")
        self.check_condition(point_template.is_shown, errors, "point not shown")
        self.check_condition(not point_template.contest.readonly_mode, errors, "score in read only mode")
        if len(errors) > 0:
            raise ValidationError(errors)

        return super(PointRecordSerializer, self).validate(attrs)

    def validate_number_point_template(self, attrs, point_template, errors):
        units_scored = attrs["units_scored"]
        uup = point_template.upper_units_bound
        lup = point_template.lower_units_bound
        self.check_condition(units_scored <= uup, errors, "units_scored > upper_unit_bound")
        self.check_condition(units_scored >= lup, errors, "units_scored < lower_unit_bound")

    def validate_checkbox_point_template(self, attrs, errors):
        units_scored = attrs["units_scored"]
        self.check_condition(units_scored in [0, 1], errors, "boolean fields should be in [0,1]")

    @staticmethod
    def check_condition(condition, errors, error_messages_id):
        if not condition:
            errors['Error'] = gettext(error_messages_id)

    def create(self, validated_data):
        request = self.context["request"]
        point_template = validated_data["point_template"]
        contest = util_methods.get_current_contest_dict(request)["id"]
        username = util_methods.get_username_from_session(request)
        validated_data["person"] = ContestPerson.objects.get(person__username=username, contest__id=contest)
        if point_template.template_type == "NumberPointTemplate":
            validated_data["point_total"] = point_template.points_per_unit * validated_data["units_scored"]
        elif point_template.template_type == "CheckboxPointTemplate":
            validated_data["point_total"] = point_template.points_if_done * validated_data["units_scored"]
        else:
            validated_data["point_total"] = 0
        point_record = PointRecord.objects.filter(person_id=validated_data["person"].id,
                                                  record_date=validated_data["record_date"],
                                                  point_template=point_template)
        if point_record.exists():
            return super(PointRecordSerializer, self).update(point_record[0], validated_data)
        else:
            return super(PointRecordSerializer, self).create(validated_data)


class UserInputPointRecordSerializer(serializers.ModelSerializer):
    record_type = serializers.ReadOnlyField()
    point_template = ContestFilteredPrimaryKeyRelatedField(helper_function_name="get_contest_point_templates",
                                                           to_repr_field="label",
                                                           to_repr_class=PointTemplate)

    class Meta:
        exclude = PointRecordSerializer.Meta.exclude
        read_only_fields = ["point_total"]
        model = UserInputPointRecord

    def validate_reviewed_by_admin(self, value):
        request = self.context["request"]
        role = util_methods.get_current_contest_dict(request)["role"]
        if role in [ContestPerson.ContestRole.ADMIN.value, ContestPerson.ContestRole.SUPER_ADMIN.value]:
            return True
        else:
            raise ValidationError(gettext("member can't review points"))

    def validate_point_total(self, value):
        if self.validate_reviewed_by_admin(True):
            return value
