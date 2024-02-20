from datetime import datetime
from gettext import gettext

from allauth.account.adapter import get_adapter
from allauth.account.forms import default_token_generator
from allauth.account.utils import user_pk_to_url_str
from rest_framework import mixins, exceptions
from rest_framework import serializers
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core import util_methods
from core.models import Person
from core.permissions import IsContestAdmin, IsContestSuperAdmin, NoPermission, IsContestMember, EmailVerified
from allauth.account.adapter import DefaultAccountAdapter


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
                errors.append({"error": _serializer.errors, "data": _serializer.initial_data})
        if len(errors) > 0:
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
                    errors.append({"error": _serializer.errors, "data": _serializer.initial_data})
            else:
                errors.append({"error": "Object not Found", "data": item})
        if len(errors) > 0:
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


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField()

    def validate(self, attrs):
        if Person.objects.filter(email=attrs["email"], username=attrs["username"]).exists():
            return attrs
        else:
            raise exceptions.ValidationError(gettext('Invalid e-mail or username'))

    def save(self):
        request = self.context.get('request')
        data = self.validated_data
        user = Person.objects.get(email=data["email"], username=data["username"])
        temp_key = default_token_generator.make_token(user)
        context = {
            'user': user,
            'key': temp_key,
            'uid': user_pk_to_url_str(user),
        }
        get_adapter(request).send_mail(
            'account/email/password_reset_key', data["email"], context
        )


class AllAuthSessionLessAdapter(DefaultAccountAdapter):
    def stash_verified_email(self, request, email):
        pass

    def unstash_verified_email(self, request):
        return None

    def stash_user(self, request, user):
        pass

    def unstash_user(self, request):
        return request.user.pk

    def is_email_verified(self, request, email):
        return False

    def pre_login(self, request, user, *, email_verification, signal_kwargs, email, signup, redirect_url):
        info = dict(email_verification=email_verification, signal_kwargs=signal_kwargs, email=email, signup=signup,
                    redirect_url=redirect_url)
        super().pre_login(request, user, **info)
        return Response("Welcome!")
