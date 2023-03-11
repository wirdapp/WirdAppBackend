from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core import models_helper, util
from core.models import Group, ContestPerson, ContestPersonGroups
from core.serializers import ContestFilteredPrimaryKeyRelatedField, PersonSerializer
from .models import *


class AutoSetContestSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        contest = util.get_current_contest_object(self.context["request"])
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
            return PersonSerializer(value.person, read_only=True, fields=["username", "first_name", "last_name"]).data
        else:
            return PersonSerializer(value.person, read_only=True).data


class PointTemplateSerializer(AutoSetContestSerializer):
    section = ContestFilteredPrimaryKeyRelatedField(object_name="sections")
    template_type = serializers.ChoiceField(choices=("number", "checkbox",), allow_blank=True, required=False)

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
        if template_type == "number":
            self.Meta.model = NumberPointTemplate
            return NumberPointTemplateSerializer(context=self.context).to_internal_value(data)
        elif template_type == "checkbox":
            self.Meta.model = CheckboxPointTemplate
            return CheckboxPointTemplateSerializer(context=self.context).to_internal_value(data)

        return super(PointTemplateSerializer, self).to_internal_value(data)


class NumberPointTemplateSerializer(AutoSetContestSerializer):
    type = serializers.ReadOnlyField()

    class Meta:
        model = NumberPointTemplate
        exclude = PointTemplateSerializer.Meta.exclude

    def validate(self, attrs):
        if not attrs["upper_units_bound"] > attrs["lower_units_bound"]:
            raise ValidationError("upper_units_bound > lower_units_bound")
        return super().validate(attrs)


class CheckboxPointTemplateSerializer(AutoSetContestSerializer):
    type = serializers.ReadOnlyField()

    class Meta:
        model = CheckboxPointTemplate
        exclude = PointTemplateSerializer.Meta.exclude


class ListCreateGroupSerializer(AutoSetContestSerializer):
    members_count = serializers.ReadOnlyField()

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
        objects = models_helper.get_group_admins(instance.id).values("username", "first_name", "last_name")
        return PersonSerializer(objects, many=True, read_only=True).data

    def get_members(self, instance):
        objects = models_helper.get_group_members(instance.id).values("username", "first_name", "last_name")
        return PersonSerializer(objects, many=True, read_only=True).data


class AddRemovePersonsToGroup(serializers.Serializer):
    persons = serializers.ListField(help_text="usernames")
    action = serializers.ChoiceField(choices=["add", "remove"], default="add")

    def validate_persons(self, data):
        contest_id = util.get_current_contest_dict(self.context)["id"]
        for username in data:
            cp = ContestPerson.objects.filter(contest_id=contest_id, person__username=username)
            if not cp.exists():
                raise ValidationError(f"No user with username {username} exists for this competition")
        return data

    def create(self, validated_data):
        contest_id = util.get_current_contest_dict(self.context)["id"]
        person_usernames = validated_data["persons"]
        group_id = validated_data["group_id"]

        if validated_data["action"] == "remove":
            ContestPersonGroups.objects \
                .filter(group_id=group_id, contest_person__person__username__in=person_usernames) \
                .delete()
        if validated_data["action"] == "add":
            group_role = 2 if validated_data["person_type"] == "admin" else 1
            defaults = dict(group_id=group_id, group_role=group_role)
            for username in person_usernames:
                contest_person_id = ContestPerson.objects.get(contest_id=contest_id, person__username=username).id
                ContestPersonGroups.objects.update_or_create(contest_person_id=contest_person_id, defaults=defaults)


class UpdateContestPersonRole(serializers.Serializer):
    contest_roles_dict = [
        ("add_moderator", 2),
        ("delete_moderator", 1,),
        ("add_super_admin", 3,),
        ("delete_super_admin", 1,),
        ("accept_participant", 1,),
        ("reject_participant", 5,),
    ]

    username = serializers.CharField()
    action = serializers.ChoiceField(choices=contest_roles_dict)

    def validate_username(self, data):
        contest_id = util.get_current_contest_dict(self.context)["id"]
        for username in data:
            cp = ContestPerson.objects.filter(contest_id=contest_id, person__username=username)
            if not cp.exists():
                raise ValidationError(f"No user with username {username} exists for this competition")
        return data

    def create(self, validated_data):
        pass
