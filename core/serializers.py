from rest_framework import serializers

from compAdmin.models import Competition


def create_general_user(competition, validated_data, general_user):
    password = validated_data.pop('password')
    user = general_user(**validated_data)
    user.set_password(password)
    user.set_competition(competition)
    user.save()
    return user


def set_competition(context, clazz):
    clazz.set_competition(context['request'].user.competition)
    clazz.save()
    return clazz


def check_if_field_valid(comp, clazz):
    return clazz.competition == comp


class CompetitionFilteredPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def __init__(self, clazz, **kwargs):
        self.clazz = clazz
        super(CompetitionFilteredPrimaryKeyRelatedField, self).__init__(**kwargs)

    def get_queryset(self):
        competition = self.context['request'].user.competition
        return self.clazz.objects.filter(competition=competition)

    def to_internal_value(self, data):
        return self.get_queryset().get(pk=data)
