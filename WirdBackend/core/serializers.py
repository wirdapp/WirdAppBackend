from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from core import util_methods
from core.models import Person, Contest, ContestPerson
from core.util_classes import DynamicFieldsCategorySerializer


class PersonSerializer(DynamicFieldsCategorySerializer):
    class Meta:
        model = Person
        fields = ['username', 'email', 'phone_number', 'first_name', 'last_name', 'profile_photo']
        read_only_fields = ['username']


class ContestSerializer(DynamicFieldsCategorySerializer):
    admin_count = serializers.ReadOnlyField()
    member_count = serializers.ReadOnlyField()
    group_count = serializers.ReadOnlyField()

    class Meta:
        fields = "__all__"
        model = Contest
