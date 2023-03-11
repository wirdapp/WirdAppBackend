from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from core.models import ContestPerson
from core.serializers import ContextFilteredPrimaryKeyRelatedField
from member_panel.models import PointRecord, UserInputPointRecord


class PointRecordSerializer(serializers.ModelSerializer):
    point_template = ContextFilteredPrimaryKeyRelatedField(object_name="point_templates")
    person = ContextFilteredPrimaryKeyRelatedField(queryset=ContestPerson.objects)

    class Meta:
        exclude = ["polymorphic_ctype"]
        model = PointRecord


class UserInputPointRecordSerializer(PointRecordSerializer):
    point_template = ContextFilteredPrimaryKeyRelatedField(object_name="point_templates")

    class Meta:
        exclude = PointRecordSerializer.Meta.exclude
        model = UserInputPointRecord


class PointTemplatePolymorphicSerializer(PolymorphicSerializer):
    resource_type_field_name = 'type'
    resource_names_matching = dict(UserInputPointRecord='user_input', PointRecord='general', )
    model_serializer_mapping = {
        UserInputPointRecord: UserInputPointRecordSerializer,
        PointRecord: PointRecordSerializer,
    }

    def to_resource_type(self, model_or_instance):
        return self.resource_names_matching[model_or_instance._meta.object_name]
