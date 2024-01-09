import datetime

from gettext import gettext
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_polymorphic.serializers import PolymorphicSerializer

from admin_panel.models import ContestCriterion, NumberCriterion, MultiCheckboxCriterion, RadioCriterion, \
    CheckboxCriterion
from core import util_methods
from core.models import ContestPerson
from core.util_classes import ContestFilteredPrimaryKeyRelatedField
from member_panel.models import PointRecord, UserInputPointRecord, NumberPointRecord, MultiCheckboxPointRecord, \
    RadioPointRecord, CheckboxPointRecord


class PointRecordSerializer(serializers.ModelSerializer):
    contest_criterion = ContestFilteredPrimaryKeyRelatedField(queryset=ContestCriterion.objects)
    timestamp = serializers.HiddenField(default=datetime.datetime.now())

    class Meta:
        model = PointRecord
        exclude = ["polymorphic_ctype"]

    def to_internal_value(self, data):
        data = data.copy()
        person = util_methods.get_current_contest_person(self.context['request'])
        data["person"] = person
        return super().to_internal_value(data)

    def validate(self, attrs):
        errors = dict()
        self.validate_date(errors, attrs)
        self.validate_mode(errors, attrs)
        self.validate_can_edit(errors, attrs)
        if errors:
            raise ValidationError(errors)
        return attrs

    def validate_date(self, errors, attrs):
        contest_criterion: ContestCriterion = attrs['contest_criterion']
        record_date = attrs['record_date']
        if record_date < contest_criterion.contest.start_date:
            errors["contest_date"] = gettext("Contest didn't start yet")
        if record_date > contest_criterion.contest.end_date:
            errors["contest_date"] = gettext("Contest already ended")

    def validate_mode(self, errors, attrs):
        contest_criterion: ContestCriterion = attrs['contest_criterion']
        if contest_criterion.contest.readonly_mode:
            errors['readonly_mode'] = gettext('Contest is readonly')

    def validate_can_edit(self, errors, attrs):
        person: ContestPerson = attrs['person']
        if person.contest_role != ContestPerson.ContestRole.MEMBER:
            errors['invalid_membership'] = gettext('User is not authorized to access contest')


class NumberPointRecordSerializer(PointRecordSerializer):
    class Meta(PointRecordSerializer.Meta):
        model = NumberPointRecord

    def validate(self, attrs):
        super().validate(attrs)
        criterion: NumberCriterion = attrs['contest_criterion']
        if attrs['number'] not in criterion.bounds:
            raise ValidationError({"bounds_error": gettext("Number entered not in bounds")})
        return attrs

    def create(self, validated_data):
        self.calculate_points(validated_data)
        return super(NumberPointRecordSerializer, self).create(validated_data)

    def update(self, record, validated_data):
        self.calculate_points(validated_data)
        return super(NumberPointRecordSerializer, self).update(record, validated_data)

    def calculate_points(self, validated_data):
        criterion: NumberCriterion = validated_data['contest_criterion']
        validated_data['point_total'] = criterion.points * validated_data['number']


class UserInputPointRecordSerializer(PointRecordSerializer):
    class Meta(PointRecordSerializer.Meta):
        model = UserInputPointRecord


class MultiCheckboxPointRecordSerializer(PointRecordSerializer):
    class Meta(PointRecordSerializer.Meta):
        model = MultiCheckboxPointRecord

    def validate(self, attrs):
        super().validate(attrs)
        criterion: MultiCheckboxCriterion = attrs['contest_criterion']
        choices: list[str] = attrs['contest_criterion']

        if not all(choice in criterion.options for choice in choices):
            raise ValidationError({'options_error': gettext('Choices entered are not valid')})
        return attrs

    def create(self, validated_data):
        self.calculate_points(validated_data)
        return super(MultiCheckboxPointRecordSerializer, self).create(validated_data)

    def update(self, record, validated_data):
        self.calculate_points(validated_data)
        return super(MultiCheckboxPointRecordSerializer, self).update(record, validated_data)

    def calculate_points(self, validated_data):
        criterion: MultiCheckboxCriterion = validated_data['contest_criterion']
        choices: list[str] = validated_data['choices']
        if criterion.partial_points:
            validated_data['point_total'] = sum(criterion.points for choice in choices
                                                if criterion.options.get(choice, False))
        else:
            validated_data['point_total'] = criterion.points if all(
                choice in criterion.options for choice in choices) else 0


class RadioPointRecordSerializer(PointRecordSerializer):
    class Meta(PointRecordSerializer.Meta):
        model = RadioPointRecord

    def validate(self, attrs):
        super().validate(attrs)
        criterion: RadioCriterion = attrs['contest_criterion']
        choice: str = attrs['criterion']

        if choice not in criterion.options:
            raise ValidationError({'options_error': gettext('Choice entered is not valid')})
        return attrs

    def create(self, validated_data):
        self.calculate_points(validated_data)
        return super(RadioPointRecordSerializer, self).create(validated_data)

    def update(self, record, validated_data):
        self.calculate_points(validated_data)
        return super(RadioPointRecordSerializer, self).update(record, validated_data)

    def calculate_points(self, validated_data):
        criterion: RadioCriterion = validated_data['contest_criterion']
        validated_data['point_total'] = criterion.points if criterion.options.get(validated_data['choice'],
                                                                                  False) else 0


class CheckboxPointRecordSerializer(PointRecordSerializer):
    class Meta(PointRecordSerializer.Meta):
        model = CheckboxPointRecord

    def create(self, validated_data):
        self.calculate_points(validated_data)
        return super(CheckboxPointRecordSerializer, self).create(validated_data)

    def update(self, record, validated_data):
        self.calculate_points(validated_data)
        return super(CheckboxPointRecordSerializer, self).update(record, validated_data)

    def calculate_points(self, validated_data):
        criterion: CheckboxCriterion = validated_data['contest_criterion']
        validated_data['point_total'] = validated_data['checked'] * criterion.points


class PolymorphicPointRecordSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        NumberPointRecord: NumberPointRecordSerializer,
        CheckboxPointRecord: CheckboxPointRecordSerializer,
        MultiCheckboxPointRecord: MultiCheckboxPointRecordSerializer,
        RadioPointRecord: RadioPointRecordSerializer,
        UserInputPointRecord: UserInputPointRecordSerializer
    }
