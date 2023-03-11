import datetime

import numpy as np
import pandas as pd
from django.db.models import Value, Sum
from django.db.models.functions import Concat
from rest_condition import And
from rest_framework import generics, views
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.permissions import IsContestAdmin, IsGroupAdmin
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
    filterset_fields = {'contest_role': ["in", "exact"],
                        'person__username': ["in", "exact"], 'person__email': ["in", "exact"],
                        'person__first_name': ["in"], 'person__last_name': ["in"]}
    serializer_class = ContestPersonSerializer
    admin_allowed_methods = []
    super_admin_allowed_methods = ['retrieve', 'list', 'update', 'partial_update']
    pagination_class = MyPageNumberPagination

    def get_queryset(self):
        current_contest = util_methods.get_current_contest_dict(self.request)["id"]
        return models_helper.get_contest_people(current_contest, contest_role=(1, 2, 3, 4))


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


class ExportResultsView(views.APIView):
    permission_classes = [And(IsAuthenticated(), IsContestAdmin(), IsGroupAdmin())]

    def get(self, request, *args, **kwargs):
        group_id = self.kwargs["group_id"]
        from_date = datetime.date.fromisoformat(request.query_params.get("from_date")) \
            if request.query_params.get("from_date") else datetime.date.today()
        to_date = datetime.date.fromisoformat(request.query_params.get("to_date")) \
            if request.query_params.get("to_date") else datetime.date.today()
        detailed_day = request.query_params.get("detailed_day", False)
        if from_date == to_date and detailed_day:
            return self.get_detailed_day(request, group_id, from_date)
        else:
            return self.get_days_results(request, group_id, from_date, to_date)

    @staticmethod
    def get_detailed_day(request, group_id, from_date):
        members = models_helper.get_group_members_contest_person_ids(group_id)
        f_name = "person__person__first_name"
        l_name = "person__person__last_name"
        points = PointRecord.objects.filter(person__id__in=members, record_date=from_date) \
            .annotate(name=Concat(f_name, Value(' '), l_name)) \
            .order_by("name", "point_template__label")

        index = points.values_list("name", flat=True).order_by("name").distinct()
        columns = points.values_list("point_template__label", flat=True).order_by("point_template__label").distinct()
        data = points.values_list("point_total", flat=True)
        data = np.reshape(data, (len(index), len(index))).tolist()
        df = pd.DataFrame(columns=columns, index=index, data=data)
        file_path = f"{group_id[-6:-1]}_{from_date}_generated_on_{datetime.date.today()}_detailed_day_results.xlsx"
        df.to_excel(file_path)
        return Response(file_path)

    @staticmethod
    def get_days_results(request, group_id, from_date, to_date):
        if (to_date - from_date).days > 30:
            return Response(gettext("can't export more than 30 days"), status=400)
        members = models_helper.get_group_members_contest_person_ids(group_id)
        username = "person__person__username"
        results = PointRecord.objects.filter(person__id__in=members, record_date__range=[from_date, to_date]) \
            .values_list(username) \
            .annotate(total_points=Sum("point_total")) \
            .values_list(username, "record_date", "total_points")
        data = dict()
        for row in results:
            date = row[1].isoformat()
            if date in data:
                data[date].update({row[0]: row[2]})
            else:
                data[date] = dict({row[0]: row[2]})
        data = pd.DataFrame(data)
        data = data.fillna(value=0)
        file_path = f"total_results_for_group_{group_id[-6:-1]}_generated_on_{datetime.date.today()}.xlsx"
        data.to_excel(file_path)
        # TODO: Cache results and return full file path
        return Response(file_path)
