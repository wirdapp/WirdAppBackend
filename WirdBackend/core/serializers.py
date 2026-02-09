from typing import cast

from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import User
from rest_framework import serializers

from core import util_methods
from core.models import Person, Contest, ContestPerson
from core.util_classes import DynamicFieldsCategorySerializer
from core.util_methods import setup_user_email


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

    def save(self,  **kwargs):
        request = self.context["request"]
        adapter = get_adapter()
        user: AbstractBaseUser = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()

        user = cast(User, adapter.save_user(request, user, self, commit=False))
        user.save()
        self.custom_signup(request, user)
        setup_user_email(user)
        return user
