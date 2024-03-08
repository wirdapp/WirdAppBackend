from core import models_helper
from core.permissions import IsGroupAdmin, IsContestOwner
from core.serializers import ContestSerializer
from core.util_classes import CustomPermissionsMixin, MyPageNumberPagination, DestroyBeforeContestStartMixin, \
    BulkCreateModelMixin
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import *


class ContestView(DestroyBeforeContestStartMixin, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsContestOwner]
    serializer_class = ContestSerializer
    destroy_message = gettext("deleting a contest will delete all users, points, groups, and results in it")

    def get_object(self):
        return util_methods.get_current_contest(self.request)


class SectionView(DestroyBeforeContestStartMixin, CustomPermissionsMixin, viewsets.ModelViewSet):
    serializer_class = SectionSerializer
    admin_allowed_methods = ['list', 'retrieve']
    super_admin_allowed_methods = ["create", "update", "partial_update", "destroy", "update_order"]
    destroy_message = gettext("deleting a section will delete all contest criteria in it")

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
    destroy_message = gettext("deleting a criterion will delete all points members recorded under it")

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


class GroupView(CustomPermissionsMixin, viewsets.ModelViewSet):
    admin_allowed_methods = ['list', 'update', 'partial_update', 'retrieve', "leaderboard"]
    super_admin_allowed_methods = ["create", "destroy"]
    serializer_class = GroupSerializer

    def get_queryset(self):
        return models_helper.get_person_enrolled_groups(self.request)

    @action(detail=True, methods=["get"])
    def leaderboard(self, request, *args, **kwargs):
        group = self.get_object()
        limit = request.query_params.get("limit", None)
        person_info = ["person__" + i for i in ["username", "first_name", "last_name", "profile_photo"]]
        leaderboard = models_helper.get_group_leaderboard(group).values("id", "total_points", *person_info)
        if limit:
            leaderboard = leaderboard[:int(limit)]
        return Response(leaderboard)


class ContestPersonGroupView(BulkCreateModelMixin, viewsets.ModelViewSet):
    permission_classes = [IsGroupAdmin]
    serializer_class = ContestPersonGroupSerializer
    pagination_class = MyPageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = {"group_role": ["in", "exact"]}
    ordering_fields = ['contest_person__person__first_name']
    search_fields = [f"contest_person__person__{field}" for field in ["first_name", "last_name", "username"]]

    def get_queryset(self):
        group_id = self.kwargs.get("group_pk")
        return ContestPersonGroup.objects.filter(group__id=group_id)

    def check_object_permissions(self, request, obj):
        user_role = util_methods.get_current_user_contest_role(request)
        obj_role = obj.contest_person.contest_role
        if user_role >= obj_role:
            self.permission_denied(request, gettext("You do not have the permission to do this action"))

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"group_id": self.kwargs["group_pk"]})
        context.update({"contest_id": self.kwargs["contest_id"]})
        return context


class ContestMembersView(CustomPermissionsMixin, viewsets.ModelViewSet):
    serializer_class = ContestPersonSerializer
    admin_allowed_methods = ["list"]
    super_admin_allowed_methods = ["create", "update", "retrieve", "partial_update", "destroy"]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = {"contest_role": ["in", "exact"], "person__username": ["exact"]}
    ordering_fields = ['person__username', "person__first_name"]
    search_fields = [f"person__{field}" for field in ["first_name", "last_name", "username"]]

    def perform_destroy(self, instance):
        # Delete groups enrollment when removing from contest
        ContestPersonGroup.objects.filter(contest_person=instance).delete()
        super().perform_destroy(instance)

    def get_queryset(self):
        contest = util_methods.get_current_contest(self.request)
        return ContestPerson.objects.filter(contest=contest)

    def check_object_permissions(self, request, obj):
        user_role = util_methods.get_current_user_contest_role(request)
        obj_role = obj.contest_role
        if user_role != 0 and user_role >= obj_role:
            self.permission_denied(request, gettext("You do not have the permission to do this action"))
