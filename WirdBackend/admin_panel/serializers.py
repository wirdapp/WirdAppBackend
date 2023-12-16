from django.utils.translation import gettext
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core import models_helper, util_methods
from core.models import Group, ContestPerson, ContestPersonGroups
from core.serializers import PersonSerializer
from core.util_classes import ContestFilteredPrimaryKeyRelatedField
from member_panel.models import UserInputPointRecord
from .models import *


class AutoSetContestSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        contest = util_methods.get_current_contest_object(self.context["request"])
        validated_data["contest"] = contest
        return super().create(validated_data)


class SectionSerializer(AutoSetContestSerializer):
    class Meta:
        model = Section
        exclude = ('contest',)


class ContestPersonSerializer(serializers.ModelSerializer):
    person = serializers.SerializerMethodField()

    class Meta:
        model = ContestPerson
        fields = ["person", "contest_role"]

    def get_person(self, value):
        if self.context["view"].action == "list":
            return PersonSerializer(value.person, read_only=True).data
        else:
            return PersonSerializer(value.person, read_only=True).data


class PointTemplateSerializer(AutoSetContestSerializer):
    section = ContestFilteredPrimaryKeyRelatedField(helper_function_name="get_contest_sections",
                                                    to_repr_class=Section, to_repr_field="label")
    template_type = serializers.ChoiceField(choices=("NumberPointTemplate", "CheckboxPointTemplate", "PointTemplate"),
                                            required=False)

    class Meta:
        model = PointTemplate
        exclude = ["contest", "polymorphic_ctype"]

    def to_representation(self, obj):
        if isinstance(obj, NumberPointTemplate):
            return NumberPointTemplateSerializer(obj, context=self.context).to_representation(obj)
        elif isinstance(obj, CheckboxPointTemplate):
            return CheckboxPointTemplateSerializer(obj, context=self.context).to_representation(obj)
        return super(PointTemplateSerializer, self).to_representation(obj)

    def to_internal_value(self, data):
        data = data.copy()
        template_type = data.pop("template_type")
        if template_type == "NumberPointTemplate":
            self.Meta.model = NumberPointTemplate
            self.context["serializer"] = NumberPointTemplateSerializer
            return NumberPointTemplateSerializer(context=self.context).to_internal_value(data)
        elif template_type == "CheckboxPointTemplate":
            self.Meta.model = CheckboxPointTemplate
            self.context["serializer"] = CheckboxPointTemplateSerializer
            return CheckboxPointTemplateSerializer(context=self.context).to_internal_value(data)
        return super(PointTemplateSerializer, self).to_internal_value(data)

    def validate(self, attrs):
        if "serializer" in self.context:
            return self.context["serializer"](context=self.context).validate(attrs)

        return super().validate(attrs)


class NumberPointTemplateSerializer(serializers.ModelSerializer):
    section = ContestFilteredPrimaryKeyRelatedField(helper_function_name="get_contest_sections",
                                                    to_repr_class=Section, to_repr_field="label")
    template_type = serializers.ReadOnlyField()

    class Meta:
        model = NumberPointTemplate
        exclude = PointTemplateSerializer.Meta.exclude

    def validate(self, attrs):
        if not attrs["upper_units_bound"] > attrs["lower_units_bound"]:
            raise ValidationError(gettext("upper_point>lower_point validation"))
        return super().validate(attrs)


class CheckboxPointTemplateSerializer(AutoSetContestSerializer):
    section = ContestFilteredPrimaryKeyRelatedField(helper_function_name="get_contest_sections",
                                                    to_repr_class=Section, to_repr_field="label")
    template_type = serializers.ReadOnlyField()

    class Meta:
        model = CheckboxPointTemplate
        exclude = PointTemplateSerializer.Meta.exclude


class ListCreateGroupSerializer(AutoSetContestSerializer):
    members_count = serializers.ReadOnlyField()
    admins_count = serializers.ReadOnlyField()

    class Meta:
        model = Group
        exclude = ('contest', "announcements")


class RetrieveUpdateGroupSerializer(AutoSetContestSerializer):
    members_count = serializers.ReadOnlyField()
    admins = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ('name', "admins", "members", "members_count")

    def get_admins(self, instance):
        objects = models_helper.get_group_admins_person_objects(instance.id) \
            .values("username", "first_name", "last_name")
        return PersonSerializer(objects, many=True, read_only=True).data

    def get_members(self, instance):
        objects = models_helper.get_group_members_person_objects(instance.id) \
            .values("username", "first_name", "last_name")
        return PersonSerializer(objects, many=True, read_only=True).data


class AddRemovePersonsToGroup(serializers.Serializer):
    persons = serializers.ListField(help_text="usernames")
    action = serializers.ChoiceField(choices=["add", "remove"], default="add")

    def validate_persons(self, data):
        contest_id = util_methods.get_current_contest(self.context)["id"]
        ids = ContestPerson.objects.filter(contest_id=contest_id, person__username__in=data).values_list("id")
        if len(data) > len(ids):
            raise ValidationError(gettext("add user to group username not in contest"))
        return ids

    def create(self, validated_data):
        person_ids = validated_data["persons"]
        group_id = validated_data["group_id"]
        action = validated_data["action"]
        if action == "remove":
            ContestPersonGroups.objects.filter(group_id=group_id, contest_person_id__in=person_ids) \
                .delete()
        elif action == "add":
            group_role = 2 if validated_data["person_type"] == "admin" else 1
            objs = [
                ContestPersonGroups(contest_person_id=pid[0], group_id=group_id, group_role=group_role)
                for pid in person_ids
            ]
            ContestPersonGroups.objects.bulk_create(objs, update_conflicts=True,
                                                    update_fields=["group_id", "group_role"],
                                                    unique_fields=["contest_person_id", "group_id"])


class UserInputRecordReviewSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ["polymorphic_ctype"]
        read_only_fields = ["person", "point_template", "record_date"]
        model = UserInputPointRecord
