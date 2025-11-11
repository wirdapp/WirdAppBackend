from drf_spectacular.utils import inline_serializer
from rest_framework import serializers

from core.serializers import PersonSerializer

UserResultsViewAPISchema = inline_serializer(
    name='UserResultsResponse',
    fields={
        'person_data': PersonSerializer(fields=["username", "first_name", "last_name"]),
        'total_points': serializers.IntegerField(allow_null=True),
        'days': serializers.ListField(
            child=inline_serializer(name='DayDetail', fields={
                'index': serializers.IntegerField(),
                'date': serializers.DateField(),
                'points': serializers.IntegerField(),
            })),
        'scores': serializers.ListField(
            child=inline_serializer(name='ScoreDetails', fields={
                'contest_criterion__id': serializers.UUIDField(),
                'contest_criterion__label': serializers.CharField(),
                'point_total': serializers.IntegerField(),
            })),
        'rank': serializers.IntegerField(allow_null=True),
    }
)

leaderboard_api_response = inline_serializer(
    name='LeaderboardResponse',
    fields={
        'leaderboard': serializers.ListField(
            child=inline_serializer(name='LeaderboardPerson', fields={
                'id': serializers.UUIDField(),
                'person__username': serializers.CharField(),
                'person__first_name': serializers.CharField(),
                'person__last_name': serializers.CharField(),
                'person__profile_photo': serializers.CharField(),
                'total_points': serializers.IntegerField(),
            })),
    }
)
