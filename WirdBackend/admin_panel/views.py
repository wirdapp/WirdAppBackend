from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import viewsets

from core import models_helper
from core.permissions import IsGroupAdmin
from core.util_classes import CustomPermissionsMixin, MyPageNumberPagination, DestroyBeforeContestStartMixin
from .serializers import *


class SectionView(DestroyBeforeContestStartMixin, CustomPermissionsMixin, viewsets.ModelViewSet):
    serializer_class = SectionSerializer
    admin_allowed_methods = ['list', 'retrieve']
    super_admin_allowed_methods = ["create", "update", "partial_update", "destroy"]

    def get_queryset(self):
        contest = util_methods.get_current_contest(self.request)
        return Section.objects.filter(contest=contest)


class ContestCriterionView(DestroyBeforeContestStartMixin, CustomPermissionsMixin, viewsets.ModelViewSet):
    admin_allowed_methods = ['list', 'retrieve']
    super_admin_allowed_methods = ['create', "update", "partial_update", "destroy"]
    serializer_class = ContestPolymorphicCriterionSerializer

    def get_queryset(self):
        contest = util_methods.get_current_contest(self.request)
        return ContestCriterion.objects.filter(contest=contest)


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
    filterset_fields = ["group__id", "group_role"]
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
    pagination_class = MyPageNumberPagination
    admin_allowed_methods = ["list"]
    super_admin_allowed_methods = ["create", "update", "retrieve", "partial_update", "destroy"]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ["contest_role", "person__username"]
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
