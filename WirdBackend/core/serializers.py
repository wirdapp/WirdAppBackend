from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from rest_framework import serializers

from core import util_methods
from core.models import Person, Contest, ContestPerson
from core.util_classes import DynamicFieldsCategorySerializer

class PersonSerializer(DynamicFieldsCategorySerializer):
    email_verified = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Person
        fields = ['username', 'email', 'phone_number', 'first_name', 'last_name', "timezone",
                  'profile_photo', "email_verified"]
        read_only_fields = ['username']

    def get_email_verified(self, person):
        return (
                EmailAddress.objects.filter(user=person, verified=True).exists()
                or SocialAccount.objects.filter(user=person).exists()
        )


class ContestSerializer(DynamicFieldsCategorySerializer):
    person_contest_role = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = "__all__"
        model = Contest

    def get_person_contest_role(self, contest):
        username = util_methods.get_username(self.context['request'])
        return ContestPerson.objects.filter(contest=contest, person__username=username).get().contest_role


import auth_kit.serializers as auth_kit_serializers  # keep it here to avoid circular imports


class CustomRegisterSerializer(auth_kit_serializers.RegisterSerializer):
    def validate_email(self, email):
        from allauth.account.adapter import get_adapter
        email = get_adapter().clean_email(email)
        return email