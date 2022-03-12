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
    def __init__(self, **kwargs):
        self.clazz = kwargs.pop('clazz') if 'clazz' in kwargs else None
        self.serializer = kwargs.pop('serializer') if 'serializer' in kwargs else None
        super(CompetitionFilteredPrimaryKeyRelatedField, self).__init__(**kwargs)

    def use_pk_only_optimization(self):
        return False

    def get_queryset(self):
        user = self.context['request'].user
        if user.is_staff:
            return self.clazz.objects.all()
        competition = user.competition
        return self.clazz.objects.filter(competition=competition)

    def to_internal_value(self, data):
        if issubclass(self.clazz, GeneralUser):
            return self.get_queryset().get(username=data)
        else:
            return self.get_queryset().get(pk=data)

    def to_representation(self, value):
        if self.serializer and self.context['request'].method == 'GET':
            return self.serializer(value).data
        elif self.pk_field is not None:
            return self.pk_field.to_representation(value.pk)
        elif issubclass(self.clazz, GeneralUser):
            return value.username
        return value.pk


class CompetitionReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        depth = 1
        fields = ('id', 'name')


class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        depth = 1
        fields = "__all__"


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
