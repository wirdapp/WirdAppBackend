from gettext import gettext

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_polymorphic.serializers import PolymorphicSerializer

from admin_panel.models import ContestCriterion, NumberCriterion, CheckboxCriterion
from admin_panel.serializers import ContestCriterionSerializer
from core import util_methods
from core.models import ContestPerson
from core.util_classes import ContestFilteredPrimaryKeyRelatedField
from member_panel.models import PointRecord, UserInputPointRecord, NumberPointRecord, MultiCheckboxPointRecord, \
    RadioPointRecord, CheckboxPointRecord


class PointRecordSerializer(serializers.ModelSerializer):
    contest_criterion = ContestFilteredPrimaryKeyRelatedField(queryset=ContestCriterion.objects, write_only=True)
    contest_criterion_data = ContestCriterionSerializer(source="contest_criterion", read_only=True,
                                                        fields=["id", "label", "points", "description",
                                                                "maximum_possible_points"])

    class Meta:
        model = PointRecord
        exclude = ["polymorphic_ctype"]

    def get_contest_criterion(self, validated_data=None):
        if validated_data and "contest_criterion" in validated_data:
            return validated_data["contest_criterion"]
        elif self.partial and self.instance:
            return self.instance.contest_criterion
        else:
            return self.fields["contest_criterion"].to_internal_value(self.initial_data["contest_criterion"])

    def to_internal_value(self, data):
        data = data.copy()
        data["person"] = self.context["person"]
        data["record_date"] = self.context["record_date"]
        return super().to_internal_value(data)

    def validate(self, attrs):
        contest = util_methods.get_current_contest(self.context['request'])
        if contest.readonly_mode:
            raise ValidationError({"contest": gettext("contest is in readonly mode")})
        return attrs

    def validate_record_date(self, value):
        contest = util_methods.get_current_contest(self.context['request'])
        if value < contest.start_date:
            raise ValidationError(gettext("Contest didn't start yet"))
        if value > contest.end_date:
            raise ValidationError(gettext("Contest already ended"))
        return value

    def validate_person(self, person):
        if person.contest_role != ContestPerson.ContestRole.MEMBER.value:
            raise ValidationError(gettext('user is not authorized to post data'))
        return person

    def create(self, validated_data):
        self.calculate_points(validated_data)
        return super(PointRecordSerializer, self).create(validated_data)

    def update(self, record, validated_data):
        self.calculate_points(validated_data)
        return super(PointRecordSerializer, self).update(record, validated_data)

    def calculate_points(self, validated_data):
        # Default implementation, can be overridden in subclasses
        raise NotImplementedError("This method should be implemented by the subclasses")


class NumberPointRecordSerializer(PointRecordSerializer):
    class Meta(PointRecordSerializer.Meta):
        model = NumberPointRecord

    def validate_number(self, value):
        criterion: NumberCriterion = self.get_contest_criterion()
        if not criterion.upper_bound >= value >= criterion.lower_bound:
            raise ValidationError(gettext("Number entered not in bounds"))
        return value

    def calculate_points(self, validated_data):
        criterion: NumberCriterion = self.get_contest_criterion(validated_data)
        validated_data['point_total'] = criterion.points * validated_data['number']


class UserInputPointRecordSerializer(PointRecordSerializer):
    class Meta(PointRecordSerializer.Meta):
        model = UserInputPointRecord

    def validate_reviewed_by_admin(self, value):
        # this should be changed by the admin
        return False

    def calculate_points(self, validated_data):
        # this should be filled by the admin
        validated_data['point_total'] = 0


class MultiCheckboxPointRecordSerializer(PointRecordSerializer):
    class Meta(PointRecordSerializer.Meta):
        model = MultiCheckboxPointRecord

    def validate_choices(self, value):
        criterion_options = [c["id"] for c in self.get_contest_criterion().options]
        if not all(choice["id"] in criterion_options for choice in value):
            raise ValidationError(gettext('Choices entered are not valid'))
        return value

    def calculate_points(self, validated_data):
        criterion = self.get_contest_criterion(validated_data)
        correct_criterion_choices = [c["id"] for c in criterion.choices if c["is_correct"]]
        user_choices = validated_data['choices']
        num_correct_answer = len(filter(lambda uc: uc in correct_criterion_choices, user_choices))
        if criterion.partial_points:
            validated_data['point_total'] = num_correct_answer * criterion.points
        else:
            validated_data['point_total'] = criterion.points \
                if num_correct_answer == len(correct_criterion_choices) else 0


class RadioPointRecordSerializer(PointRecordSerializer):
    class Meta(PointRecordSerializer.Meta):
        model = RadioPointRecord

    def validate_choice(self, value):
        criterion = self.get_contest_criterion()
        criterion_choices = [c["id"] for c in criterion.choices]
        if value not in criterion_choices:
            raise ValidationError(gettext('Choice entered is not valid'))
        return value

    def calculate_points(self, validated_data):
        criterion = self.get_contest_criterion(validated_data)
        user_choice = validated_data['choice']
        correct_criterion_choice = next(filter(lambda c: c["is_correct"], criterion.choices))
        validated_data['point_total'] = criterion.points * correct_criterion_choice["id"] == user_choice


class CheckboxPointRecordSerializer(PointRecordSerializer):
    class Meta(PointRecordSerializer.Meta):
        model = CheckboxPointRecord

    def calculate_points(self, validated_data):
        criterion: CheckboxCriterion = self.get_contest_criterion(validated_data)
        validated_data['point_total'] = validated_data['checked'] * criterion.points


class PolymorphicPointRecordSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        NumberPointRecord: NumberPointRecordSerializer,
        CheckboxPointRecord: CheckboxPointRecordSerializer,
        MultiCheckboxPointRecord: MultiCheckboxPointRecordSerializer,
        RadioPointRecord: RadioPointRecordSerializer,
        UserInputPointRecord: UserInputPointRecordSerializer
    }
