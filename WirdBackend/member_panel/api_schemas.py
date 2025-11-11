from drf_spectacular.utils import inline_serializer
from rest_framework import serializers

from core.serializers import PersonSerializer
import admin_panel.api_schemas

announcements_api_response = inline_serializer(
    name='AnnouncementResponse',
    fields={
        'announcements': serializers.ListField(
            child=inline_serializer(name='Announcement', fields={
                'date': serializers.DateField(),
                'text': serializers.IntegerField(),
                'source': serializers.ChoiceField(choices=['group', 'contest']),
            })),
    }
)

leaderboard_api_response = admin_panel.api_schemas.leaderboard_api_response