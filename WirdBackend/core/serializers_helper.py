from rest_framework import serializers

from core import util


class ContextFilteredPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        contest = util.get_current_contest_dict(request)
        queryset = super(ContextFilteredPrimaryKeyRelatedField, self).get_queryset()
        if not request or not queryset:
            return None
        queryset = queryset.filter(contest__id=contest["id"])
        return queryset

