from django.utils.translation import gettext
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import viewsets, mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from core import util_methods, models_helper
from core.serializers import *
from core.util_classes import MyModelViewSet


class ContestView(MyModelViewSet):
    serializer_class = ContestSerializer
    name = 'create-contest-view'
    member_allowed_methods = ['switch_contest', 'retrieve', 'list']
    admin_allowed_methods = ['switch_contest', 'retrieve', 'list']
    super_admin_allowed_methods = ['switch_contest', 'retrieve', 'list', 'update', 'partial_update']

    def get_queryset(self):
        username = util_methods.get_username_from_session(self.request)
        return models_helper.get_person_contests_queryset(username)

    @swagger_auto_schema(request_body=no_body,
                         responses={200: "contest switched successfully",
                                    404: "person is not enrolled in this contest"},
                         manual_parameters=[openapi.Parameter('contest_id', openapi.IN_QUERY,
                                                              description="uuid of the new contest",
                                                              type=openapi.TYPE_STRING)])
    @action(detail=False, methods=['post'])
    def switch_contest(self, request, *args, **kwargs):
        contests = self.get_queryset()
        new_contest = request.data["contest_id"]
        if contests.filter(contest__id=new_contest).exists():
            return Response(gettext("contest switched successfully"), status=status.HTTP_200_OK)
        else:
            return Response(gettext("person is not enrolled in this contest"), status=status.HTTP_404_NOT_FOUND)


class SignUpView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        user_type = self.request.query_params.get("type", "participant")
        if user_type == "participant":
            return ParticipantSignupSerializer
        elif user_type == "creator":
            return CreatorSignupSerializer

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('type', openapi.IN_QUERY, enum=['creator', 'participant'], type=openapi.TYPE_STRING)])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class CurrentContestPersonView(MyModelViewSet):
    serializer_class = PersonSerializer
    member_allowed_methods = ['retrieve', 'update', 'partial_update']
    admin_allowed_methods = []
    super_admin_allowed_methods = []

    def get_object(self):
        username = util_methods.get_username_from_session(self.request)
        return Person.objects.get(username=username)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        person = self.get_serializer(instance)
        current_contest = util_methods.get_current_contest_dict(self.request)
        data = dict(person=person.data, contest=current_contest)
        return Response(data)
