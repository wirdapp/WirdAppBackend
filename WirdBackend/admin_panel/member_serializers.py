from member_panel.serializers import *
from rest_framework.exceptions import ValidationError


class AdminPointRecordSerializer(PointRecordSerializer):
    def to_internal_value(self, data):
        data = data.copy()
        data["person"] = self.context['person']
        data["record_date"] = self.context["date"]
        return super().to_internal_value(data)

    def validate_can_edit(self, errors, attrs):
        # TODO: Check if current_user is super admin or a group admin of that student
        pass


class AdminNumberPointRecordSerializer(AdminPointRecordSerializer, NumberPointRecordSerializer):
    pass


class AdminUserInputPointRecordSerializer(AdminPointRecordSerializer, UserInputPointRecordSerializer):
    pass


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
