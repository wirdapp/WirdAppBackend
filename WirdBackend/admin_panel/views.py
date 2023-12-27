from django.core.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from core import models_helper
from core.util_classes import MyModelViewSet, MyPageNumberPagination
from .serializers import *


class SectionView(MyModelViewSet):
    serializer_class = SectionSerializer
    admin_allowed_methods = ['list', 'retrieve']
    super_admin_allowed_methods = ["create", "update", "partial_update", "delete"]

    def get_queryset(self):
        contest_id = util_methods.get_current_contest_id_from_session(self.request)
        return models_helper.get_contest_sections(contest_id)


class ContestCriterionView(MyModelViewSet):
    admin_allowed_methods = ['list', 'retrieve']
    super_admin_allowed_methods = ['create', "update", "partial_update", "delete"]
    serializer_class = ContestPolymorphicCriterionSerializer

    def get_queryset(self):
        contest_id = util_methods.get_current_contest_id_from_session(self.request)
        return models_helper.get_contest_point_templates(contest_id)


class GroupView(MyModelViewSet):
    admin_allowed_methods = ['list', 'update', 'partial_update', 'retrieve']
    super_admin_allowed_methods = ["create", "add_or_remove_members"]
    serializer_class = GroupSerializer

    def get_queryset(self):
        return models_helper.get_current_user_managed_groups(self.request)


class ContestPersonGroupView(MyModelViewSet):
    serializer_class = ContestPersonGroupSerializer
    admin_allowed_methods = ["list", "create", "destroy"]
    filterset_fields = ["group__id", "group_role"]
    pagination_class = MyPageNumberPagination

    def get_queryset(self):
        managed_groups = models_helper.get_current_user_managed_groups(self.request).values("id")
        return ContestPersonGroup.objects.filter(group__id__in=managed_groups)


class ContestPersonView(MyModelViewSet):
    admin_allowed_methods = ["list"]
    super_admin_allowed_methods = ["create", "update", "retrieve", "partial_update", "destroy"]
    serializer_class = ContestPersonSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["contest_role", "person__username"]
    ordering_fields = ['person__username']
    pagination_class = MyPageNumberPagination

    def get_queryset(self):
        contest_id = util_methods.get_current_contest_id_from_session(self.request)
        return ContestPerson.objects.filter(contest__id=contest_id)

    def check_object_permissions(self, request, obj):
        user_role = util_methods.get_current_user_role_from_session(request)
        obj_role = obj.contest_role
        if user_role >= obj_role:
            raise PermissionDenied
