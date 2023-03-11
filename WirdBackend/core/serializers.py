from rest_framework import serializers

from core import util
from core.models import Person, Contest, ContestPerson


class PersonSerializer(serializers.ModelSerializer):
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


class AutoSetContestSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        contest = util.get_contest(self.context["request"])
        validated_data["contest"] = contest
        return super().create(validated_data)


class CreatorSignupSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["name"]
        model = Contest


class ParticipantSignupSerializer(serializers.ModelSerializer):
    access_code = serializers.CharField(max_length=6, min_length=6, write_only=True)

    class Meta:
        fields = ["access_code", "username", "password", 'first_name', 'last_name', 'profile_photo', 'phone_number',
                  'email']
        model = Person

    def create(self, validated_data):
        access_code = validated_data.pop('access_code').lower()
        contest = Contest.objects.get(id__endswith=access_code)
        if contest:
            person = super().create(validated_data)
            ContestPerson.objects.create(person=person, contest=contest, contest_role=4)
        else:
            raise serializers.ValidationError({"access_code": "Access Code is not correct"})
        return person
