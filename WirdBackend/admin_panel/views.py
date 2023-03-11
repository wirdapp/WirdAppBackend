from collections import OrderedDict

from django.db.models import Sum, Value
from django.db.models.functions import Concat
from rest_condition import And
from rest_framework import generics, views
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.permissions import IsContestAdmin, IsGroupAdmin
from core.util_classes import MyModelViewSet
from member_panel.models import PointRecord
from member_panel.serializers import PointRecordSerializer
from .serializers import *


class SectionView(MyModelViewSet):
    serializer_class = SectionSerializer
    name = 'section-list'
    lookup_field = 'id'
    admin_allowed_methods = ['list', 'retrieve']

    def get_queryset(self):
        contest_id = util_methods.get_current_contest_dict(self.request)["id"]
        return models_helper.get_contest_sections(contest_id)


class PointTemplatesView(MyModelViewSet):
    name = 'points-templates-list'
    lookup_field = 'id'
    admin_allowed_methods = ['list', 'retrieve']
    serializer_class = PointTemplateSerializer

    def get_queryset(self):
        contest_id = util_methods.get_current_contest_dict(self.request)["id"]
        return models_helper.get_contest_point_templates(contest_id)


class GroupView(MyModelViewSet):
    name = 'contest-group-list'
    lookup_field = 'id'
    admin_allowed_methods = ['list', 'update', 'partial_update', 'retrieve', "add_or_remove_member"]
    super_admin_allowed_methods = MyModelViewSet.super_admin_allowed_methods + ["add_or_remove_admin",
                                                                                "add_or_remove_member"]

    def get_serializer_class(self):
        if self.action in ["list", "create"]:
            return ListCreateGroupSerializer
        elif self.action in ["retrieve", "update", "partial_update"]:
            return RetrieveUpdateGroupSerializer
        elif self.action in ["add_or_remove_admin", "add_or_remove_member"]:
            return AddRemovePersonsToGroup

    def get_queryset(self):
        username = util_methods.get_username_from_session(self.request)
        current_contest = util_methods.get_current_contest_dict(self.request)["id"]
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
            return Response(gettext("user added to the group"), status=200)
        else:
            return Response({**serializer.errors}, status=400)


class ContestPersonView(MyModelViewSet):
    name = 'contest-people'
    lookup_field = 'person__username'
    filterset_fields = {'contest_role': ["in", "exact"]}
    serializer_class = ContestPersonSerializer
    admin_allowed_methods = []
    super_admin_allowed_methods = ['retrieve', 'list', 'update', 'partial_update']

    def get_queryset(self):
        current_contest = util_methods.get_current_contest_dict(self.request)["id"]
        return models_helper.get_contest_people(current_contest, contest_role=(1, 2, 3, 4, 5))


class TopMembers(views.APIView):
    permission_classes = [And(IsAuthenticated(), IsContestAdmin()), ]

    def get(self, request, *args, **kwargs):
        contest_id = util_methods.get_current_contest_dict(request)["id"]
        first_name = "person__person__first_name"
        last_name = "person__person__last_name"
        top_members = PointRecord.objects.filter(person__contest__id=contest_id) \
                          .annotate(name=Concat(first_name, Value(' '), last_name)) \
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


class ResultsView(views.APIView):
    permission_classes = [And(IsAuthenticated(), IsContestAdmin())]

    def get(self, request, *args, **kwargs):
        date = kwargs.get("date", None)
        contest_id = util_methods.get_current_contest_dict(request)["id"]
        username = util_methods.get_username_from_session(request)
        group_list = models_helper.get_person_managed_groups(username, contest_id).values_list("id", "name")
        result = []
        for group in group_list:
            group_people = models_helper.get_group_members_contest_person_ids(group[0])
            submitted = PointRecord.objects.filter(person__id__in=group_people, record_date=date) \
                .order_by("person_id").distinct('person_id').count()
            not_submitted = len(group_people) - submitted
            data = dict(group_id=group[0], group_name=group[1], submitted=submitted, not_submitted=not_submitted)
            result.append(data)
        return Response(result)


class GroupMemberResultsView(generics.ListAPIView):
    permission_classes = [And(IsAuthenticated(), IsContestAdmin(), IsGroupAdmin())]

    def get_queryset(self):
        group_id = self.kwargs["group_id"]
        members = ContestPersonGroups.objects.prefetch_related("contest_person__person") \
            .filter(group_id=group_id, group_role=1)
        return members

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        date = self.kwargs["date"]
        paginated_queryset = self.paginate_queryset(queryset)
        results = list()
        for member in paginated_queryset:
            results.append(self.get_member_results(member, date))
        return self.get_paginated_response(results)

    @staticmethod
    def get_member_results(member, date):
        user_name = member.contest_person.person.username
        points = list(PointRecord.objects.filter(person__id=member.contest_person_id, record_date=date))
        points = PointRecordSerializer(points, many=True, read_only=True).data
        total_day = sum([point["point_total"] for point in points])
        return dict(username=user_name, points=points, total_day=total_day)
