from admin_panel.models import ContestPersonGroup
from core.models_helper import get_person_enrolled_groups
from member_panel.serializers import *
from rest_framework.exceptions import ValidationError


class AdminPointRecordSerializer(PointRecordSerializer):

    def validate(self, attrs):
        user_role = util_methods.get_current_user_contest_role(self.context["request"])
        managed_groups = get_person_enrolled_groups(self.context["request"])
        person_to_edit = self.context["person"]
        in_admin_group = ContestPersonGroup.objects.filter(group__in=managed_groups,
                                                           contest_person__id=person_to_edit).exists()
        if not (user_role <= ContestPerson.ContestRole.SUPER_ADMIN.value or in_admin_group):
            raise ValidationError(gettext("you do not have permission to edit the points of this person"))
        return attrs

    def validate_record_date(self, value):
        contest = util_methods.get_current_contest(self.context['request'])
        today = datetime.date.today()
        if value < contest.start_date:
            raise ValidationError(gettext("Contest didn't start yet"))
        if value > contest.end_date:
            raise ValidationError(gettext("Contest already ended"))
        if value > today:
            raise ValidationError(gettext("you can't record in the future"))
        return value


class AdminNumberPointRecordSerializer(AdminPointRecordSerializer, NumberPointRecordSerializer):
    pass


class AdminUserInputPointRecordSerializer(AdminPointRecordSerializer, UserInputPointRecordSerializer):
    def validate_reviewed_by_admin(self, value):
        return value

    def calculate_points(self, validated_data):
        validated_data['point_total'] = validated_data["point_total"]


class AdminMultiCheckboxPointRecordSerializer(AdminPointRecordSerializer, MultiCheckboxPointRecordSerializer):
    pass


class AdminRadioPointRecordSerializer(AdminPointRecordSerializer, RadioPointRecordSerializer):
    pass


class AdminCheckboxPointRecordSerializer(AdminPointRecordSerializer, CheckboxPointRecordSerializer):
    pass


class AdminPolymorphicPointRecordSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        NumberPointRecord: AdminNumberPointRecordSerializer,
        CheckboxPointRecord: AdminCheckboxPointRecordSerializer,
        MultiCheckboxPointRecord: AdminMultiCheckboxPointRecordSerializer,
        RadioPointRecord: AdminRadioPointRecordSerializer,
        UserInputPointRecord: AdminUserInputPointRecordSerializer
    }
