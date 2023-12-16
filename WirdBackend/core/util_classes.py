from datetime import datetime

from rest_condition import And
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from core import util_methods, models_helper
from core.permissions import IsContestAdmin, IsContestSuperAdmin, NoPermission, IsContestMember, EmailVerified
from enum import Enum
from rest_framework.throttling import UserRateThrottle


class BurstRateThrottle(UserRateThrottle):
    scope = 'join_contest'


class DateConverter:
    regex = '[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}'
    format = '%Y-%m-%d'

    def to_python(self, value):
        return datetime.strptime(value, self.format).date()

    def to_url(self, value):
        return value.strftime(self.format)


class MyPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 10


class MyModelViewSet(viewsets.ModelViewSet):
    authenticated_allowed_methods = []
    verified_allowed_methods = []
    member_allowed_methods = []
    verified_members_allowed_methods = []
    admin_allowed_methods = []
    super_admin_allowed_methods = []

    def get_permissions(self):
        if self.action in self.authenticated_allowed_methods:
            return IsAuthenticated(),
        if self.action in self.verified_allowed_methods:
            return And(IsAuthenticated(), EmailVerified()),
        if self.action in self.member_allowed_methods:
            return And(IsAuthenticated(), IsContestMember()),
        if self.action in self.verified_members_allowed_methods:
            return And(IsAuthenticated(), EmailVerified(), IsContestMember()),
        if self.action in self.admin_allowed_methods:
            return And(IsAuthenticated(), IsContestAdmin()),
        if self.action in self.super_admin_allowed_methods:
            return And(IsAuthenticated(), IsContestSuperAdmin()),
        return NoPermission(),


class DynamicFieldsCategorySerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)
        if fields is None and self.fields is None:
            self.fields = "__all__"

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class ContestFilteredPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):

    def __init__(self, **kwargs):
        self.helper_function_name = kwargs.pop("helper_function_name", None)
        self.to_repr_field = kwargs.pop("to_repr_field", None)
        self.to_repr_class = kwargs.pop("to_repr_class", None)
        super().__init__(**kwargs)

    def get_queryset(self):
        request = self.context.get('request', None)
        contest = util_methods.get_current_contest(request)
        if self.helper_function_name:
            func = getattr(models_helper, self.helper_function_name)
            queryset = func(contest["id"])
        else:
            queryset = super(ContestFilteredPrimaryKeyRelatedField, self).get_queryset()
            queryset = queryset.filter(contest__id=contest["id"])
        return queryset

    def to_representation(self, value):
        if self.to_repr_class:
            label = getattr(self.to_repr_class.objects.get(pk=value.pk), self.to_repr_field)
            pk = value.pk
            # TODO: Remove this ugly line, it's only used for HTML API
            if 'view' in self.context and hasattr(self.context["view"], 'action') and self.context["view"].action in \
                    ["create", "update", "partial_update"]:
                return pk
            else:
                return dict(id=pk, label=label)
        else:
            return super(ContestFilteredPrimaryKeyRelatedField, self).to_representation(value)
