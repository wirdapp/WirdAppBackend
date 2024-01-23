from django.utils.translation import gettext
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core import models_helper, util_methods
from core.models import ContestPerson
from core.serializers import *
from core.util_classes import CustomPermissionsMixin


class ContestView(CustomPermissionsMixin, viewsets.ModelViewSet):
    authenticated_allowed_methods = ['join_contest', 'list']
    verified_allowed_methods = ['create']
    member_allowed_methods = ['retrieve']
    serializer_class = ContestSerializer
    lookup_url_kwarg = "contest_id"

    def perform_create(self, serializer):
        contest = serializer.save()
        username = self.request.user.username
        person = Person.objects.get(username=username)
        ContestPerson.objects.create(person=person, contest=contest, contest_role=0)
        return contest

    @action(detail=False, methods=['post'])
    def join_contest(self, request):
        try:
            contest_id = request.data.get('contest_id', "")
            contest = Contest.objects.get(contest_id=contest_id, readonly_mode=False)
            person_id = Person.objects.get(username=util_methods.get_username(request)).id
            ContestPerson.objects.get_or_create(person_id=person_id, contest=contest, contest_role=3)
            return Response(gettext("joined the new contest"), 200)
        except Contest.DoesNotExist:
            return Response(gettext("cannot join this contest or access code is wrong"), 400)

    def get_queryset(self):
        username = util_methods.get_username(self.request)
        return models_helper.get_person_contests(username)

    serializer_fields = dict(
        list=["id", "contest_id", "name", "contest_photo"],
        create=["contest_id", "name", "description", "contest_photo", "start_date", "end_date"],
        join_contest=["contest_id"],
    )

    def get_object(self):
        return util_methods.get_current_contest(self.request)

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(*args, fields=self.serializer_fields.get(self.action, None), **kwargs)


class CurrentUserView(generics.RetrieveUpdateAPIView):
    serializer_class = PersonSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        return user
