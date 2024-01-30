from datetime import datetime
from gettext import gettext

from allauth.account.models import EmailAddress
from rest_condition import And
from rest_framework import mixins, exceptions
from rest_framework import serializers
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core import util_methods
from core.permissions import IsContestAdmin, IsContestSuperAdmin, NoPermission, IsContestMember, EmailVerified


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
        if self.action in self.verified_members_allowed_methods:
            return And(EmailVerified(), IsContestMember()),
        if self.action in self.admin_allowed_methods:
            return IsContestAdmin(),
        if self.action in self.super_admin_allowed_methods:
            return IsContestSuperAdmin(),
        return NoPermission(),


class BulkCreateModelMixin:
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer
        data = request.data if isinstance(request.data, list) else [request.data]
        for item in data:
            _serializer = serializer(data=item)
            _serializer.is_valid(raise_exception=True)
            self.perform_create(_serializer)
        return Response(f"Created {len(data)} items", status=status.HTTP_201_CREATED)


class DestroyBeforeContestStartMixin(mixins.DestroyModelMixin):
    def destroy(self, request, *args, **kwargs):
        contest = util_methods.get_current_contest(request)
        if datetime.today().date() >= contest.start_date:
            raise exceptions.MethodNotAllowed(gettext("cannot edit contest after its start date"))

        return super().destroy(request, *args, **kwargs)


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


class ResendEmailConfirmation(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        EmailAddress.objects.get(user=request.user).send_confirmation(request)
        return Response({'message': 'Email confirmation sent'}, status=status.HTTP_201_CREATED)
