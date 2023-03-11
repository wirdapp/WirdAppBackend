from rest_framework import serializers

from admin_panel.models import PointTemplate
from core.models import ContestPerson
from core.util_classes import ContestFilteredPrimaryKeyRelatedField
from member_panel.models import PointRecord, UserInputPointRecord


class PointRecordSerializer(serializers.ModelSerializer):
    point_template = ContestFilteredPrimaryKeyRelatedField(helper_function_name="point_templates",
                                                           to_repr_field="label",
                                                           to_repr_class=PointTemplate)
    person = ContestFilteredPrimaryKeyRelatedField(queryset=ContestPerson.objects)
    record_type = serializers.ChoiceField(choices=["user_input", ], allow_blank=True, required=False)

    class Meta:
        exclude = ["polymorphic_ctype"]
        model = PointRecord

    def to_representation(self, obj):
        if isinstance(obj, UserInputPointRecord):
            return UserInputPointRecordSerializer(obj, context=self.context).to_representation(obj)
        return super(PointRecordSerializer, self).to_representation(obj)

    def to_internal_value(self, data):
        data = data.copy()
        record_type = data.pop("record_type")
        if record_type == "user_input":
            self.Meta.model = UserInputPointRecord
            return UserInputPointRecordSerializer(context=self.context).to_internal_value(data)
        return super(PointRecordSerializer, self).to_internal_value(data)


class UserInputPointRecordSerializer(serializers.ModelSerializer):
    record_type = serializers.ReadOnlyField()
    point_template = ContestFilteredPrimaryKeyRelatedField(helper_function_name="point_templates",
                                                           to_repr_field="label",
                                                           to_repr_class=PointTemplate)

    class Meta:
        exclude = PointRecordSerializer.Meta.exclude
        model = UserInputPointRecord
