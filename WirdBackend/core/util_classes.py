import logging
from datetime import datetime

from rest_framework import serializers
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core import util_methods
from core.permissions import IsContestAdmin, IsContestSuperAdmin, NoPermission, IsContestMember, EmailVerified

logger = logging.getLogger('django')


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
    max_page_size = 20


class CustomPermissionsMixin:
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
            return EmailVerified(),
        if self.action in self.member_allowed_methods:
            return IsContestMember(),
        if self.action in self.admin_allowed_methods:
            return IsContestAdmin(),
        if self.action in self.super_admin_allowed_methods:
            return IsContestSuperAdmin(),
        return NoPermission(),


class BulkCreateModelMixin:
    def create(self, request, *args, **kwargs):
        errors = []
        created = []
        serializer = self.get_serializer
        data = request.data if isinstance(request.data, list) else [request.data]
        for item in data:
            _serializer = serializer(data=item)
            is_valid = _serializer.is_valid(raise_exception=False)
            if is_valid:
                self.perform_create(_serializer)
                created.append(_serializer.data)
            else:
                logger.error("BulkCreate validation error: %s | data: %s", _serializer.errors, _serializer.initial_data)
                errors.append({"error": _serializer.errors, "data": _serializer.initial_data})
        if len(errors) > 0:
            logger.warning("BulkCreate completed with %d error(s) and %d created: %s", len(errors), len(created), errors)
            return Response({"created": created, "errors": errors}, status=207)
        return Response(created, status=status.HTTP_201_CREATED)


class BulkUpdateModelMixin:
    def bulk_update(self, request, *args, **kwargs):
        errors = []
        updated = []
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer
        data = request.data if isinstance(request.data, list) else [request.data]
        for item in data:
            instance = self.get_object(item)
            if instance:
                _serializer = serializer(instance, data=item, partial=partial)
                _is_valid = _serializer.is_valid(raise_exception=True)
                if _is_valid:
                    self.perform_update(_serializer)
                    updated.append(_serializer.data)
                    if getattr(instance, '_prefetched_objects_cache', None):
                        instance._prefetched_objects_cache = {}
                else:
                    logger.error("BulkUpdate validation error: %s | data: %s", _serializer.errors, _serializer.initial_data)
                    errors.append({"error": _serializer.errors, "data": _serializer.initial_data})
            else:
                logger.error("BulkUpdate object not found for data: %s", item)
                errors.append({"error": "Object not Found", "data": item})
        if len(errors) > 0:
            logger.warning("BulkUpdate completed with %d error(s) and %d updated: %s", len(errors), len(updated), errors)
            return Response({"updated": updated, "errors": errors}, status=207)
        return Response(updated, status=status.HTTP_200_OK)

    def get_object(self, item):
        queryset = self.filter_queryset(self.get_queryset())
        try:
            obj = queryset.get(pk=item["id"])
        except queryset.model.DoesNotExist:
            return None
        self.check_object_permissions(self.request, obj)
        return obj


class DynamicFieldsCategorySerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

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
        super().__init__(**kwargs)

    def get_queryset(self):
        contest = util_methods.get_current_contest(self.context['request'])
        queryset = super(ContestFilteredPrimaryKeyRelatedField, self).get_queryset()
        queryset = queryset.filter(contest=contest)
        return queryset
