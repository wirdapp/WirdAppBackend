from rest_framework import serializers

from compAdmin.models import Competition


def create_general_user(competition, validated_data, general_user):
    password = validated_data.pop('password')
    user = general_user(**validated_data)
    user.set_password(password)
    user.set_competition(competition)
    user.save()
    return user


def set_competition(competition, clazz):
    clazz.set_competition(competition)
    return clazz


def check_if_field_valid(comp, clazz):
    return clazz.competition == comp


class CompetitionQuerySet(serializers.RelatedField):
    def __init__(self, clazz):
        self.clazz = clazz
        super().__init__()

    def get_queryset(self):
        return self.clazz.objects.filter(competition=self.context['request'].user.competition)
