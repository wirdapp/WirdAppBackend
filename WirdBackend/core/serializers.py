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
