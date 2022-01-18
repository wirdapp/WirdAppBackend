from rest_framework import serializers
from .models import *


class PointTemplateSerializer(serializers.ModelSerializer):
    competition = serializers.CharField(source='competition.id', read_only=True)

    class Meta:
        model = PointTemplate
        depth = 1
        fields = '__all__'


class CompGroupSerializer(serializers.ModelSerializer):
    competition = serializers.CharField(source='competition.id', read_only=True)

    class Meta:
        model = CompGroup
        depth = 1
        fields = '__all__'
