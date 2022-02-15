from rest_framework import serializers

from compAdmin.models import Competition
from core.models import GeneralUser
from student.models import StudentUser


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

    def to_representation(self, value):
        if self.pk_field is not None:
            return self.pk_field.to_representation(value.pk)
        if isinstance(value, GeneralUser):
            return value.username
        return value.pk


class CompetitionReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        depth = 1
        exclude = ('show_standings', 'readonly_mode')


class TopStudentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentUser
        depth = 1
        fields = ['username', 'first_name', 'last_name', 'profile_photo', 'total_points']
        extra_kwargs = {'username': {'read_only': True}, 'first_name': {'read_only': True},
                        'last_name': {'read_only': True},
                        'profile_photo': {'read_only': True},
                        'total_points': {'read_only': True},
                        }
