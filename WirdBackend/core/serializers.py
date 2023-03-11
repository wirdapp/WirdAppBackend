from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from core.models import Person, Contest, ContestPerson
from core.util_classes import DynamicFieldsCategorySerializer


class PersonSerializer(DynamicFieldsCategorySerializer):
    class Meta:
        model = Person
        fields = ['username', 'email', 'phone_number', 'first_name', 'last_name', 'profile_photo']
        read_only_fields = ['username']


class ContestSerializer(serializers.ModelSerializer):
    access_code = serializers.ReadOnlyField()
    admin_count = serializers.ReadOnlyField()
    member_count = serializers.ReadOnlyField()
    group_count = serializers.ReadOnlyField()

    class Meta:
        fields = "__all__"
        model = Contest


class CreatorSignupSerializer(serializers.ModelSerializer):
    contest_name = serializers.CharField(min_length=5, max_length=128, write_only=True)

    class Meta:
        fields = ["contest_name", "username", "password", 'first_name', 'last_name', 'profile_photo', 'phone_number',
                  'email']
        model = Person

    def create(self, validated_data):
        contest_name = validated_data.pop('contest_name')
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


