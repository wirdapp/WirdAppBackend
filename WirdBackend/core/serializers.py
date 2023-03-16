from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from core.models import Person, Contest
from core.util_classes import DynamicFieldsCategorySerializer


class PersonSerializer(DynamicFieldsCategorySerializer):
    class Meta:
        model = Person
        fields = ['username', 'email', 'phone_number', 'first_name', 'last_name', 'profile_photo']
        read_only_fields = ['username']


class BasicContestSerializer(serializers.ModelSerializer):
    access_code = serializers.ReadOnlyField()

    class Meta:
        fields = ["id", "name", "access_code"]
        model = Contest


class ExtendedContestSerializer(serializers.ModelSerializer):
    access_code = serializers.ReadOnlyField()
    admin_count = serializers.ReadOnlyField()
    member_count = serializers.ReadOnlyField()
    group_count = serializers.ReadOnlyField()

    class Meta:
        fields = "__all__"
        model = Contest


class PersonSignupSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["username", "password", 'first_name', 'last_name', 'profile_photo', 'phone_number',
                  'email']
        model = Person

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        person = super().create(validated_data)
        return person
