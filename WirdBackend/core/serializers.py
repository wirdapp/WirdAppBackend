from core import util_methods
from core.models import Person, Contest, ContestPerson
from core.util_classes import DynamicFieldsCategorySerializer
from rest_framework import serializers
from allauth.account.models import EmailAddress


class PersonSerializer(DynamicFieldsCategorySerializer):
    email_verified = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Person
        fields = ['username', 'email', 'phone_number', 'first_name', 'last_name', "timezone",
                  'profile_photo', "email_verified"]
        read_only_fields = ['username']

    def get_email_verified(self, person):
        return EmailAddress.objects.filter(user=person, verified=True).exists()


class ContestSerializer(DynamicFieldsCategorySerializer):
    person_contest_role = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = "__all__"
        model = Contest

    def get_person_contest_role(self, contest):
        username = util_methods.get_username(self.context['request'])
        return ContestPerson.objects.filter(contest=contest, person__username=username).get().contest_role
