from rest_framework import serializers

from compAdmin.models import Competition, CompGroup
from core.serializers import create_general_user, CompetitionQuerySet
from .models import *


class PointRecordSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = PointRecord
        depth = 1
        fields = '__all__'


class StudentUserSerializer(serializers.ModelSerializer):
    competition = serializers.PrimaryKeyRelatedField(queryset=Competition.objects.all(), source="competition.id")

    class Meta:
        model = StudentUser
        depth = 2
        fields = ['username', 'password', 'first_name', 'last_name', 'total_points', 'read_only', 'competition',
                  ]
        extra_kwargs = {'password': {'write_only': True}, 'total_points': {'read_only': True}}

    def create(self, validated_data):
        competition = validated_data.pop('competition')['id']
        return create_general_user(competition, validated_data, StudentUser)
