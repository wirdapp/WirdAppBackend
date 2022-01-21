from rest_framework import serializers

from compAdmin.models import Competition


def create_general_user(competition, validated_data, general_user):
    password = validated_data.pop('password')
    user = general_user(**validated_data)
    user.set_password(password)
    user.set_competition(competition)
    user.save()
    return user


def set_competition(competition, validated_data, clazz):
    clazz = clazz(**validated_data)
    clazz.set_competition(competition)
    clazz.save()
    return clazz


class CompetitionQuerySet(serializers.RelatedField):
    def __init__(self, clazz):
        self.clazz = clazz
        super().__init__()

    def get_queryset(self):
        return self.clazz.objects.filter(competition=self.context['request'].user.competition)
