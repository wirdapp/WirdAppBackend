from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from core import util
from core.models import Person, Contest, ContestPerson


class DynamicFieldsCategorySerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class PersonSerializer(DynamicFieldsCategorySerializer):
    class Meta:
        model = Person
        fields = ['id', 'username', 'email', 'phone_number', 'first_name', 'last_name', 'profile_photo']


class ContestSerializer(serializers.ModelSerializer):
    access_code = serializers.ReadOnlyField()

    class Meta:
        fields = "__all__"
        model = Contest


class ContestPersonSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = ContestPerson


class CreatorSignupSerializer(serializers.ModelSerializer):
    contest_name = serializers.CharField(min_length=5, max_length=128, write_only=True)

    class Meta:
        fields = ["contest_name", "username", "password", 'first_name', 'last_name', 'profile_photo', 'phone_number',
                  'email']
        model = Person

    def create(self, validated_data):
        contest_name = validated_data.pop('contest_name').lower()
        contest = Contest.objects.create(name=contest_name)
        validated_data['password'] = make_password(validated_data['password'])
        person = super().create(validated_data)
        ContestPerson.objects.create(person=person, contest=contest, contest_role=3)
        return person


class ParticipantSignupSerializer(serializers.ModelSerializer):
    access_code = serializers.CharField(min_length=6, max_length=6, write_only=True)

    class Meta:
        fields = ["access_code", "username", "password", 'first_name', 'last_name', 'profile_photo', 'phone_number',
                  'email']
        model = Person

    def create(self, validated_data):
        access_code = validated_data.pop('access_code').lower()
        contest = Contest.objects.get(id__endswith=access_code)
        validated_data['password'] = make_password(validated_data['password'])
        if contest:
            person = super().create(validated_data)
            ContestPerson.objects.create(person=person, contest=contest, contest_role=4)
        else:
            raise serializers.ValidationError({"access_code": "Access Code is not correct"})
        return person


class AutoSetContestSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        contest = util.get_current_contest_object(self.context["request"])
        validated_data["contest"] = contest
        return super().create(validated_data)


class ContextFilteredPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        contest = util.get_current_contest_dict(request)
        queryset = super(ContextFilteredPrimaryKeyRelatedField, self).get_queryset()
        if not request or not queryset:
            return None
        queryset = queryset.filter(contest__id=contest["id"])
        return queryset


class MyRelatedField(serializers.RelatedField):
    display_value_fields = {"id"}

    def to_internal_value(self, data):
        return self.get_queryset().get(pk=data)

    def to_representation(self, value):
        return getattr(value, "id")

    def display_value(self, instance):
        values = []
        for field in self.display_value_fields:
            try:
                values.append(getattr(instance, field))
            except:
                values.append("")

        return " ".join(values)

    def get_queryset(self):
        raise NotImplementedError(
            '{cls}.to_internal_value() must be implemented for field '
            '{field_name}.'.format(
                cls=self.__class__.__name__,
                field_name=self.field_name,
            )
        )
