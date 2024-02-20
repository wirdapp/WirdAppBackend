import datetime

from WirdBackend.settings import settings
from core import models_helper
from core.serializers import *
from core.util_classes import CustomPermissionsMixin
from django.db.models import Count
from django.utils.translation import gettext
from member_panel.models import PointRecord
from rest_framework import permissions
from rest_framework import viewsets, views
from rest_framework.decorators import action
from rest_framework.response import Response
from allauth.account.adapter import get_adapter
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit


class ContestView(CustomPermissionsMixin, viewsets.ModelViewSet):
    authenticated_allowed_methods = ['join_contest', 'list']
    verified_allowed_methods = ['create']
    member_allowed_methods = ['retrieve']
    serializer_class = ContestSerializer
    lookup_url_kwarg = "contest_id"

    def perform_create(self, serializer):
        contest = serializer.save()
        username = self.request.user.username
        person = Person.objects.get(username=username)
        ContestPerson.objects.create(person=person, contest=contest, contest_role=0)
        return contest

    @action(detail=False, methods=['post'])
    def join_contest(self, request):
        try:
            contest_id = request.data.get('contest_id', "")
            contest = Contest.objects.get(contest_id=contest_id, readonly_mode=False)
            person_id = Person.objects.get(username=util_methods.get_username(request)).id
            ContestPerson.objects.get_or_create(person_id=person_id, contest=contest, contest_role=3)
            return Response(gettext("joined the new contest"), 200)
        except Contest.DoesNotExist:
            return Response(gettext("cannot join this contest or access code is wrong"), 400)

    def get_queryset(self):
        username = util_methods.get_username(self.request)
        return models_helper.get_person_contests(username)

    serializer_fields = dict(
        list=["id", "contest_id", "name", "contest_photo", "person_contest_role"],
        create=["contest_id", "name", "description", "contest_photo", "country", "start_date", "end_date"],
        join_contest=["contest_id"],
    )

    def get_object(self):
        return util_methods.get_current_contest(self.request)

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(*args, fields=self.serializer_fields.get(self.action, None), **kwargs)


class DeleteUserView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["delete"]

    @staticmethod
    def delete(request, *args, **kwargs):
        instance = request.user
        instance.is_active = False
        instance.save()
        response = Response(status=204)
        response.delete_cookie(settings.REST_AUTH["JWT_AUTH_COOKIE"])
        response.delete_cookie(settings.REST_AUTH["JWT_AUTH_REFRESH_COOKIE"])
        return response


class ResendEmailConfirmation(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        EmailAddress.objects.get(user=request.user).send_confirmation(request)
        return Response({'message': 'Email confirmation sent'}, status=201)


class UsernameResetView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @method_decorator(ratelimit(key='ip', rate='1/d', method='POST'))
    def post(self, request, *args, **kwargs):
        try:
            email = request.data.get("email", "")
            usernames = list(EmailAddress.objects.filter(email=email).values_list("user__username", flat=True))
            context = {"usernames": usernames}
            get_adapter(request).send_mail('account/email/username_reset', email, context)
        except Exception as e:
            pass  # for security reasons
        return Response(gettext("email sent"))


class GeneralStatsView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        members_count = Person.objects.count()
        contest_count = Contest.objects.count()
        today = datetime.date.today()
        last_week = util_methods.get_dates_between_two_dates(today - datetime.timedelta(days=7), today)
        submission_count = PointRecord.objects.filter(record_date__in=last_week).count()
        countries = (Contest.objects.values("country").annotate(country_count=Count('country'))
                     .values("country", "country_count"))
        data = dict(members_count=members_count, contest_count=contest_count,
                    submission_count=submission_count, countries=countries)
        return Response(data)
