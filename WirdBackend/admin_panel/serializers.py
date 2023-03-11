from rest_framework import serializers

from core.serializers import AutoSetContestSerializer
from core.serializers_helper import ContextFilteredPrimaryKeyRelatedField
from .models import *


class SectionSerializer(AutoSetContestSerializer):
    class Meta:
        model = Section
        exclude = ('contest',)


class PointTemplateSerializer(AutoSetContestSerializer):
    section = ContextFilteredPrimaryKeyRelatedField(queryset=Section.objects)

    class Meta:
        model = PointTemplate
        depth = 2
        exclude = ('contest',)


class GroupSerializer(AutoSetContestSerializer):
    members_count = serializers.ReadOnlyField()

    class Meta:
        model = Group
        exclude = ('contest', "announcements")
        read_only_fields = ('members_count',)
