from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core import models_helper
from core.permissions import IsGroupAdmin
from core.util_classes import CustomPermissionsMixin, MyPageNumberPagination, DestroyBeforeContestStartMixin
from .serializers import *


class SectionView(DestroyBeforeContestStartMixin, CustomPermissionsMixin, viewsets.ModelViewSet):
    serializer_class = SectionSerializer
    admin_allowed_methods = ['list', 'retrieve']
    super_admin_allowed_methods = ["create", "update", "partial_update", "destroy", "update_order"]

    def get_queryset(self):
        contest = util_methods.get_current_contest(self.request)
        return Section.objects.filter(contest=contest)

    @action(detail=False, methods=["post"])
    def update_order(self, request, *args, **kwargs):
        sections_data = request.data.get('sections', [])
        section_updates = [Section(id=section["id"], position=section["position"]) for section in sections_data]
        no_of_updates = Section.objects.bulk_update(section_updates, fields=['position'])
        return Response(f"{gettext('updated the order of sections successfully')} {no_of_updates}")


class ContestCriterionView(DestroyBeforeContestStartMixin, CustomPermissionsMixin, viewsets.ModelViewSet):
    admin_allowed_methods = ['list', 'retrieve']
    super_admin_allowed_methods = ['create', "update", "partial_update", "destroy", "update_order"]
    serializer_class = ContestPolymorphicCriterionSerializer

    def get_queryset(self):
        contest = util_methods.get_current_contest(self.request)
        return ContestCriterion.objects.filter(contest=contest)

    @action(detail=False, methods=["post"])
    def update_order(self, request, *args, **kwargs):
        criteria_data = request.data.get('criteria', [])
        criteria_updates = [ContestCriterion(id=criterion["id"], order_in_section=criterion["order_in_section"])
                            for criterion in criteria_data]
        no_of_updates = ContestCriterion.objects.bulk_update(criteria_updates, fields=['order_in_section'])
        return Response(f"{gettext('updated the order of criteria successfully')} {no_of_updates}")


class GroupView(DestroyBeforeContestStartMixin, CustomPermissionsMixin, viewsets.ModelViewSet):
    admin_allowed_methods = ['list', 'update', 'partial_update', 'retrieve']
    super_admin_allowed_methods = ["create", "destroy"]
    serializer_class = GroupSerializer

    def get_queryset(self):
        return models_helper.get_current_user_managed_groups(self.request)


class ContestPersonGroupView(viewsets.ModelViewSet):
    permission_classes = [IsGroupAdmin]
    serializer_class = ContestPersonGroupSerializer
    pagination_class = MyPageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = {"group_role": ["in"]}
    ordering_fields = ['contest_person__person__first_name']
    search_fields = [f"contest_person__person__{field}" for field in ["first_name", "last_name", "username"]]
    lookup_field = "contest_person__person__username"

    def get_queryset(self):
        group_id = self.kwargs.get("group_pk")
        return ContestPersonGroup.objects.filter(group__id=group_id)

    def check_object_permissions(self, request, obj):
        user_role = util_methods.get_current_user_contest_role(request)
        obj_role = obj.contest_role
        if user_role >= obj_role:
            self.permission_denied(request, gettext("You do not have the permission to do this action"))


class ContestMembersView(CustomPermissionsMixin, viewsets.ModelViewSet):
    serializer_class = ContestPersonSerializer
    admin_allowed_methods = ["list"]
    super_admin_allowed_methods = ["create", "update", "retrieve", "partial_update", "destroy"]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = {"contest_role": ["in"], "person__username": ["exact"]}
    ordering_fields = ['person__username', "person__first_name"]
    search_fields = [f"person__{field}" for field in ["first_name", "last_name", "username"]]
    lookup_field = "person__username"

    def get_queryset(self):
        contest = util_methods.get_current_contest(self.request)
        return ContestPerson.objects.filter(contest=contest)

    def check_object_permissions(self, request, obj):
        user_role = util_methods.get_current_user_contest_role(request)
        obj_role = obj.contest_role
        if user_role != 0 and user_role >= obj_role:
            self.permission_denied(request, gettext("You do not have the permission to do this action"))
