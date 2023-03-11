from collections import OrderedDict

from django.db.models import Sum, Value
from django.db.models.functions import Concat
from rest_condition import And
from rest_framework import views
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.my_view import MyModelViewSet
from core.permissions import IsContestAdmin
from core.serializers import PersonSerializer
from member_panel.models import PointRecord
from .serializers import *


class SectionView(MyModelViewSet):
    serializer_class = SectionSerializer
    name = 'section-list'
    lookup_field = 'id'
    queryset = Section.objects
    admin_allowed_methods = ['list', 'retrieve']


class PointTemplatesView(MyModelViewSet):
    name = 'points-templates-list'
    lookup_field = 'id'
    admin_allowed_methods = ['list', 'retrieve']
    serializer_class = PointTemplateSerializer

    def get_queryset(self):
        contest_id = util.get_current_contest_dict(self.request)["id"]
        return models_helper.get_contest_point_templates(contest_id)


class GroupView(MyModelViewSet):
    name = 'contest-group-list'
    lookup_field = 'id'
    admin_allowed_methods = ['list', 'update', 'partial_update', 'retrieve', "add_or_remove_member"]
    super_admin_allowed_methods = ['list', 'update', 'partial_update', 'retrieve',
                                   "add_or_remove_admin", "add_or_remove_member"]

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
        return self.add_remove_person(request, person_type, kwargs["id"])

    @action(methods=["post"], detail=True)
    def add_or_remove_member(self, request, *args, **kwargs):
        person_type = "member"
        return self.add_remove_person(request, person_type, kwargs["id"])

    @staticmethod
    def add_remove_person(request, person_type, group_id):
        serializer = AddRemovePersonsToGroup(data=request.data, context=request)
        if serializer.is_valid():
            serializer.validated_data["person_type"] = person_type
            serializer.validated_data["group_id"] = group_id
            serializer.create(serializer.validated_data)
            return Response("Created!", status=200)
        else:
            return Response({**serializer.errors}, status=400)


class ContestPersonView(MyModelViewSet):
    name = 'contest-people'
    lookup_field = 'person__username'
    serializer_class = ContestPersonSerializer

    def get_queryset(self):
        current_contest = util.get_current_contest_dict(self.request)["id"]
        return models_helper.get_contest_people(current_contest)


class TopMembers(views.APIView):
    permission_classes = [And(IsAuthenticated(), IsContestAdmin()), ]

    def get(self, request, *args, **kwargs):
        contest_id = util.get_current_contest_dict(request)["id"]
        top_members = PointRecord.objects.filter(person__contest__id=contest_id) \
                          .annotate(name=Concat("person__person__first_name", Value(' '), "person__person__last_name")) \
                          .values("person_id", 'name') \
                          .annotate(total_points=Sum("point_total")).order_by("-total_points")[:5]

        results = list(PointRecord.objects.filter(person_id__in=top_members.values_list("person_id"))
                       .values('record_date', 'person_id')
                       .order_by('-record_date')
                       .annotate(total_daily_points=Sum("point_total")))

        user_results = OrderedDict()
        for member in top_members:
            user_results[member["person_id"]] = {'name': member["name"], 'total': member["total_points"]}

        for result in results:
            person_id = result['person_id']
            user_results[person_id].update({str(result['record_date']): result['total_daily_points']})

        return Response(user_results)
