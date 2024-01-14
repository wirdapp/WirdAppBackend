from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_polymorphic.serializers import PolymorphicSerializer

from core import util_methods
from core.serializers import PersonSerializer
from core.util_classes import ContestFilteredPrimaryKeyRelatedField
from .models import *


class AutoSetContestSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        data = data.copy()
        contest = util_methods.get_current_contest(self.context['request'])
        data["contest"] = contest
        return super().to_internal_value(data)


class SectionSerializer(AutoSetContestSerializer):
    class Meta:
        model = Section
        fields = "__all__"


class ContestCriterionSerializer(AutoSetContestSerializer):
    section = ContestFilteredPrimaryKeyRelatedField(queryset=Section.objects)

    class Meta:
        model = ContestCriterion
        exclude = ['polymorphic_ctype']


class NumberCriterionSerializer(ContestCriterionSerializer):
    class Meta(ContestCriterionSerializer.Meta):
        model = NumberCriterion


class CheckboxCriterionSerializer(ContestCriterionSerializer):
    class Meta(ContestCriterionSerializer.Meta):
        model = CheckboxCriterion


class MultiCheckboxCriterionSerializer(ContestCriterionSerializer):
    class Meta(ContestCriterionSerializer.Meta):
        model = MultiCheckboxCriterion


class RadioCriterionSerializer(ContestCriterionSerializer):
    class Meta(ContestCriterionSerializer.Meta):
        model = RadioCriterion


class UserInputCriterionSerializer(ContestCriterionSerializer):
    class Meta(ContestCriterionSerializer.Meta):
        model = UserInputCriterion


class ContestPolymorphicCriterionSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        NumberCriterion: NumberCriterionSerializer,
        CheckboxCriterion: CheckboxCriterionSerializer,
        MultiCheckboxCriterion: MultiCheckboxCriterionSerializer,
        RadioCriterion: RadioCriterionSerializer,
        UserInputCriterion: UserInputCriterionSerializer
    }


class ContestPersonSerializer(AutoSetContestSerializer):
    person = serializers.PrimaryKeyRelatedField(queryset=Person.objects, write_only=True)
    person_info = PersonSerializer(source="person", read_only=True,
                                   fields=["id", "username", "first_name", "last_name"])
    username = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = ContestPerson
        fields = '__all__'
        extra_kwargs = {'contest': {'write_only': True}}

    def validate_contest_role(self, role):
        user_role = util_methods.get_current_user_contest_role(self.context["request"])
        if user_role >= role:
            raise ValidationError(gettext("you can't use this role of this user"))
        return role

    def to_internal_value(self, data):
        data = data.copy()
        username = data.pop("username", "")
        if username:
            person = get_object_or_404(Person, username=username).pk
            data["person"] = person
        return super().to_internal_value(data)


class GroupSerializer(AutoSetContestSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class ContestPersonGroupSerializer(serializers.ModelSerializer):
    contest_person = ContestFilteredPrimaryKeyRelatedField(queryset=ContestPerson.objects, write_only=True)
    group = ContestFilteredPrimaryKeyRelatedField(write_only=True, queryset=Group.objects)
    person = PersonSerializer(read_only=True, source="contest_person.person",
                              fields=["id", "username", "first_name", "last_name"])
    username = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = ContestPersonGroup
        fields = '__all__'

    def validate(self, attr):
        user_role = util_methods.get_current_user_contest_role(self.context["request"])
        if ContestPersonGroup.objects.filter(contest_person=attr["contest_person"], group=attr["group"]).exists():
            raise ValidationError({"contest_person": gettext("member already in group")})
        if user_role <= ContestPerson.ContestRole.SUPER_ADMIN.value:
            raise ValidationError({"contest_person": gettext("super admins and owners can't be added to a group")})
        if attr["role"] == 1 and user_role > 1:
            raise ValidationError({"role": gettext("only super admins can assign group admin")})
        return attr

    def to_internal_value(self, data):
        data = data.copy()
        data["group"] = self.context.get("view").kwargs.get("group_pk")
        username = data.pop("username", None)
        if username:
            person_id = get_object_or_404(ContestPerson, person__username=username).uuid
            data["contest_person"] = person_id
        return super().to_internal_value(data)
