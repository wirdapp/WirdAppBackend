from core.models import Person, Contest
from core.util_classes import DynamicFieldsCategorySerializer
from rest_framework import serializers
from allauth.account.models import EmailAddress


class PersonSerializer(DynamicFieldsCategorySerializer):
    email_verified = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Person
        fields = ['username', 'email', 'phone_number', 'first_name', 'last_name', 'profile_photo', "email_verified"]
        read_only_fields = ['username']

    def get_email_verified(self, person):
        return EmailAddress.objects.filter(user=person, verified=True).exists()


class ContestSerializer(DynamicFieldsCategorySerializer):
    class Meta:
        fields = "__all__"
        model = Contest
