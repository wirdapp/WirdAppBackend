import datetime
import os.path

import pandas as pd
from django.contrib.auth.hashers import make_password
from django.db.models import Sum
from rest_condition import And
from rest_framework import generics, views, mixins, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.models import Person
from core.permissions import *
from core.util_classes import MyModelViewSet, MyPageNumberPagination
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
    pagination_class = MyPageNumberPagination

    def get_queryset(self):
        contest_id = util_methods.get_current_contest_dict(self.request)["id"]
        return models_helper.get_contest_point_templates(contest_id)


class GroupView(MyModelViewSet):
    name = 'contest-group-list'
    lookup_field = 'id'
    admin_allowed_methods = ['list', 'update', 'partial_update', 'retrieve', "add_or_remove_member"]
    super_admin_allowed_methods = MyModelViewSet.super_admin_allowed_methods + ["add_or_remove_admin",
                                                                                "add_or_remove_member"]
    pagination_class = MyPageNumberPagination

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
    filter_backends = [filters.SearchFilter]
    search_fields = ["person__username", "person__first_name", "person__last_name", "person__email"]
    serializer_class = ContestPersonSerializer
    admin_allowed_methods = []
    super_admin_allowed_methods = ['retrieve', 'list', 'update', 'partial_update']
    pagination_class = MyPageNumberPagination

    def get_queryset(self):
        contest_role = self.request.query_params.getlist('contest_role', (1, 2, 3, 4, 5, 6))
        current_contest = util_methods.get_current_contest_dict(self.request)["id"]
        return models_helper.get_contest_people(current_contest, contest_role=contest_role)


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


class GroupMembersResultsView(generics.ListAPIView):
    permission_classes = [And(IsAuthenticated(), IsContestAdmin(), IsGroupAdmin())]
    pagination_class = MyPageNumberPagination

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


class ReviewUserInputPoints(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    permission_classes = [And(IsAuthenticated(), IsContestAdmin()), ]
    serializer_class = UserInputRecordReviewSerializer
    filterset_fields = ["reviewed_by_admin", 'record_date', "person__person__username"]

    def get_queryset(self):
        contest_id = util_methods.get_current_contest_dict(self.request)["id"]
        return UserInputPointRecord.objects.filter(point_template__contest__id=contest_id)


class ResetMemberPassword(views.APIView):
    permission_classes = [And(IsAuthenticated(), IsContestAdmin(), MemberBelongsToAdminGroups())]

    def get(self, request, *args, **kwargs):
        return Response(gettext("post person username and new password"))

    def post(self, request, *args, **kwargs):
        username = request.data["username"]
        password = request.data["password"]
        if not (username and password):
            Response(gettext("post person username and new password"), status=400)
        password = make_password(password)
        Person.objects.filter(username="username").update(password=password)
        return Response(gettext("password updated by admin"), status=200)


def process_dataframe(file_path, results):
    data = dict()
    for row in results:
        if str(row[1]) in data:
            data[str(row[1])].update({row[0]: row[2]})
        else:
            data[str(row[1])] = dict({row[0]: row[2]})
    data = pd.DataFrame(data)
    data = data.fillna(value=0)
    data.to_excel(file_path)


def process_export_request(request, members, file_path):
    from_date = request.query_params.get("from_date", None)
    to_date = request.query_params.get("to_date", None)
    if not (from_date and to_date):
        return Response(gettext("from_date and to_date param should be provided"), status=400)
    from_date = datetime.date.fromisoformat(from_date)
    to_date = datetime.date.fromisoformat(to_date)
    if (to_date - from_date).days > 30:
        return Response(gettext("can't export more than 30 days"), status=400)
    results = PointRecord.objects.filter(person__id__in=members, record_date__range=[from_date, to_date]) \
        .values_list("person__person__username") \
        .annotate(total_points=Sum("point_total")) \
        .values_list("person__person__username", "record_date", "total_points")
    if results.count() == 0:
        return Response(gettext("no data to extract"))
    process_dataframe(file_path, results)
    return Response(file_path)


class ExportGroupResultsView(views.APIView):
    permission_classes = [And(IsAuthenticated(), IsContestAdmin(), IsGroupAdmin())]

    def get(self, request, *args, **kwargs):
        group_id = self.kwargs["group_id"]
        file_path = f"total_results_for_group_{group_id[-6:-1]}_generated_on_{datetime.date.today()}.xlsx"
        if os.path.exists(file_path):
            return Response(f"{gettext('data was generated today under url')} {file_path}")
        members = models_helper.get_group_members_contest_person_ids(group_id)
        return process_export_request(request, members, file_path)


class ExportAllResultsView(views.APIView):
    permission_classes = [And(IsAuthenticated(), IsContestSuperAdmin)]

    def get(self, request, *args, **kwargs):
        current_contest = util_methods.get_current_contest_dict(request)["id"]
        file_path = f"total_results_for_contest_{current_contest[-6:-1]}_generated_on_{datetime.date.today()}.xlsx"
        if os.path.exists(file_path):
            return Response(f"{gettext('data was generated today under url')} {file_path}")
        members = models_helper.get_contest_people(current_contest, contest_role=[1])
        return process_export_request(request, members, file_path)
