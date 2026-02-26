from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_polymorphic.serializers import PolymorphicSerializer

from core import util_methods
from core.serializers import PersonSerializer
from core.util_classes import ContestFilteredPrimaryKeyRelatedField, DynamicFieldsCategorySerializer
from .models import *


class AutoSetContestSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        data = data.copy()
        contest = util_methods.get_current_contest(self.context['request'])
        data["contest"] = contest.id
        return super().to_internal_value(data)


class SectionSerializer(DynamicFieldsCategorySerializer, AutoSetContestSerializer):
    class Meta:
        model = Section
        fields = "__all__"


class ContestCriterionSerializer(DynamicFieldsCategorySerializer, AutoSetContestSerializer):
    section = ContestFilteredPrimaryKeyRelatedField(queryset=Section.objects, write_only=True)
    section_info = SectionSerializer(source="section", fields=["id", "label", "position"], read_only=True)
    maximum_possible_points = serializers.ReadOnlyField()

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
        user_to_add_role = attr["contest_person"].contest_role
        current_user_role = util_methods.get_current_user_contest_role(self.context['request'])
        if ContestPersonGroup.objects.filter(contest_person=attr["contest_person"], group=attr["group"]).exists():
            raise ValidationError({"contest_person": gettext("member already in group")})
        if attr["group_role"] == 1 and current_user_role > 1:
            raise ValidationError({"contest_person": gettext("only super admins can assign group admins")})
        if attr["group_role"] == 1 and user_to_add_role != 2:
            raise ValidationError({"contest_person": gettext("only admins are allowed to become group admins")})
        if attr["group_role"] == 2 and user_to_add_role not in [3, 4]:
            raise ValidationError({"contest_person": gettext("only members are allowed to become group members")})
        return attr

    def to_internal_value(self, data):
        data = data.copy()
        data["group"] = self.context.get("group_id")
        username = data.pop("username", None)
        if username and username[0].strip() != '':
            person_id = get_object_or_404(ContestPerson, person__username=username).id
            data["contest_person"] = person_id
        return super().to_internal_value(data)


class ExportJobSerializer(serializers.ModelSerializer):
    group_id = ContestFilteredPrimaryKeyRelatedField(
        queryset=Group.objects, required=False, allow_null=True, source='group'
    )
    member_ids = serializers.ListField(
        child=serializers.UUIDField(), required=False, allow_null=True, allow_empty=False
    )

    class Meta:
        model = ExportJob
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'status', 'serialized_data', 'group']
        extra_kwargs = {
            'members_from': {'required': False, 'allow_null': True, 'min_value': 1},
            'members_to': {'required': False, 'allow_null': True, 'min_value': 1},
        }

    def validate(self, attrs):
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        group = attrs.get('group')
        member_ids = attrs.get('member_ids')
        members_from = attrs.get('members_from')
        members_to = attrs.get('members_to')

        if start_date > end_date:
            raise ValidationError(gettext("validation_start_date_after_end_date"))

        if (end_date - start_date).days > 31:
            raise ValidationError(gettext("validation_date_range_exceeds_31_days"))

        contest = self.context['contest']
        if start_date < contest.start_date or end_date > contest.end_date:
            raise ValidationError(
                gettext("validation_dates_outside_contest_range")
                % {
                    'start': contest.start_date,
                    'end': contest.end_date
                }
            )

        has_group = group is not None
        has_member_ids = member_ids is not None and len(member_ids) > 0
        has_member_range = members_from is not None or members_to is not None

        selections = sum([has_group, has_member_ids, has_member_range])

        if selections == 0:
            raise ValidationError(gettext("validation_selection_required"))

        if selections > 1:
            raise ValidationError(gettext("validation_multiple_selections_not_allowed"))

        if has_member_range:
            if members_from is None or members_to is None:
                raise ValidationError(gettext("validation_member_range_requires_both_bounds"))

            if members_from > members_to:
                raise ValidationError(gettext("validation_invalid_member_range_order"))

            if (members_to - members_from + 1) > 250:
                raise ValidationError(gettext("validation_member_range_exceeds_250"))

        return attrs

