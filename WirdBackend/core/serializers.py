from core.models import Person, Contest
from core.util_classes import DynamicFieldsCategorySerializer


class PersonSerializer(DynamicFieldsCategorySerializer):
    class Meta:
        model = Person
        fields = ['username', 'email', 'phone_number', 'first_name', 'last_name', 'profile_photo']
        read_only_fields = ['username']


class ContestSerializer(DynamicFieldsCategorySerializer):
    class Meta:
        fields = "__all__"
        model = Contest
