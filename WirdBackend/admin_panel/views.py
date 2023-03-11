from rest_framework.decorators import action
from rest_framework.response import Response

from core.my_view import MyModelViewSet
from core.serializers import PersonSerializer
from .serializers import *


class SectionView(MyModelViewSet):
    serializer_class = SectionSerializer
    name = 'section-list'
    lookup_field = 'id'
    queryset = Section.objects
    admin_allowed_methods = ['list', 'retrieve']


class PointTemplatesView(MyModelViewSet):
    serializer_class = PointTemplateSerializer
    name = 'points-templates-list'
    lookup_field = 'id'
    queryset = PointTemplate.objects
    admin_allowed_methods = ['list', 'retrieve']


class GroupView(MyModelViewSet):
    name = 'contest-group-list'
    lookup_field = 'id'
    admin_allowed_methods = ['list', 'update', 'partial_update', 'retrieve']
    super_admin_allowed_methods = ['list', 'update', 'partial_update', 'retrieve']

    def get_serializer_class(self):
        if self.action in ["list", "create"]:
            return ListCreateGroupSerializer
        elif self.action in ["retrieve", "update", "partial_update"]:
            return RetrieveUpdateGroupSerializer
        elif self.action in ["add_or_remove_admin", "add_or_remove_member"]:
            return AddRemovePersonsToGroup

    def get_queryset(self):
        username = util.get_username_from_session(self.request)
        current_contest = util.get_current_contest_dict(self.request)["id"]
        return models_helper.get_person_managed_groups(username, current_contest)

    @action(methods=["post"], detail=True)
    def add_or_remove_admin(self, request, *args, **kwargs):
        person_type = "admin"
        return self.add_remove_person(request, person_type, self.get_object())

    @action(methods=["post"], detail=True)
    def add_or_remove_member(self, request, *args, **kwargs):
        person_type = "member"
        return self.add_remove_person(request, person_type, self.get_object())

    @staticmethod
    def add_remove_person(request, person_type, group):
        serializer = AddRemovePersonsToGroup(data=request.data, context=request)
        if serializer.is_valid():
            serializer.validated_data["person_type"] = person_type
            serializer.validated_data["group"] = group
            serializer.create(serializer.validated_data)
            return Response("Created!", status=200)
        else:
            return Response({**serializer.errors}, status=400)


class ContestPeopleView(MyModelViewSet):
    name = 'contest-people'
    lookup_field = 'id'
    serializer_class = PersonSerializer

    def get_queryset(self):
        current_contest = util.get_current_contest_dict(self.request)["id"]
        return models_helper.get_contest_people(current_contest).values("id", "username", "first_name", "last_name")
