import datetime
import random
import string

from django.core.cache import cache
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Value, Sum, F
from django.db.models.functions import Concat
from django.template.loader import render_to_string
from django.utils.translation import get_language
from django.utils.translation import gettext
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema, no_body
from hijri_converter import Gregorian
from rest_condition import And
from rest_framework import viewsets, mixins, permissions, status, views
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core import util_methods, models_helper
from core.models import ContestPerson
from core.permissions import IsContestMember
from core.serializers import *
from core.util_classes import MyModelViewSet
from member_panel.models import PointRecord


class ContestView(MyModelViewSet):
    serializer_class = BasicContestSerializer
    name = 'create-contest-view'
    member_allowed_methods = ['switch_contest', 'retrieve', 'list', "current_contest"]
    admin_allowed_methods = ['switch_contest', 'retrieve', 'list', "current_contest"]
    super_admin_allowed_methods = ['switch_contest', 'retrieve', 'list', "current_contest"]

    def get_queryset(self):
        username = util_methods.get_username_from_session(self.request)
        return models_helper.get_person_contests_queryset(username)

    @action(detail=False, methods=['post'])
    def switch_contest(self, request, *args, **kwargs):
        contests = self.get_queryset()
        new_contest = request.data["contest_id"]
        if contests.filter(id=new_contest).exists():
            util_methods.update_current_contest_dict(request, new_contest)
            return Response(gettext("contest switched successfully"), status=status.HTTP_200_OK)
        else:
            return Response(gettext("person is not enrolled in this contest"), status=status.HTTP_404_NOT_FOUND)

    @action(url_path="current", detail=False)
    def current_contest(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def get_object(self):
        current_contest = util_methods.get_current_contest_object(self.request)
        if current_contest:
            return current_contest
        else:
            return Contest.objects.none()


class SignUpView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = PersonSignupSerializer


class CurrentContestPersonView(MyModelViewSet):
    serializer_class = PersonSerializer
    member_allowed_methods = ['retrieve', 'update', 'partial_update']
    contest_related = False

    def get_object(self):
        username = util_methods.get_username_from_session(self.request)
        return Person.objects.get(username=username)


class TopMembersOverall(views.APIView):
    permission_classes = [And(IsAuthenticated(), IsContestMember()), ]

    def get(self, request, *args, **kwargs):
        contest_id = util_methods.get_current_contest_dict(request)["id"]
        results = cache.get(contest_id)
        if not results:
            first_name = "person__person__first_name"
            last_name = "person__person__last_name"
            username = "person__person__username"
            results = PointRecord.objects.filter(person__contest__id=contest_id, person__contest_role__in=[1, 4]) \
                .annotate(username=F(username), name=Concat(first_name, Value(' '), last_name)) \
                .values("username", "person_id", 'name') \
                .annotate(total_points=Sum("point_total")).order_by("-total_points")
            cache.set(contest_id, results, 60 * 10)

        return Response(results)


class TopMembersByDate(views.APIView):
    permission_classes = [And(IsAuthenticated(), IsContestMember()), ]

    def get(self, request, *args, **kwargs):
        contest_id = util_methods.get_current_contest_dict(request)["id"]
        date = kwargs["date"]
        key = f"{contest_id}_{date}"
        results = cache.get(key)
        if not results:
            first_name = "person__person__first_name"
            last_name = "person__person__last_name"
            username = "person__person__username"
            results = PointRecord.objects.filter(record_date=date,
                                                 person__contest__id=contest_id,
                                                 person__contest_role__in=[1, 4]) \
                .annotate(username=F(username), name=Concat(first_name, Value(' '), last_name)) \
                .values("username", "person_id", 'name') \
                .annotate(total_daily_points=Sum("point_total")) \
                .order_by('-total_daily_points')
            cache.set(key, results, 60 * 10)

        return Response(results)


class CalendarView(views.APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        results = []
        today = datetime.datetime.today().date()
        lang = get_language()
        date = kwargs.get('date', None)
        if date:
            if date == "today":
                return Response(self.get_date_dict(0, lang, today))
            else:
                return Response(self.get_date_dict(0, lang, datetime.date.fromisoformat(date)))
        for delta in range(-15, 15):
            date_dict = self.get_date_dict(delta, lang, today)
            results.append(date_dict)

        return Response(results)

    @staticmethod
    def get_date_dict(delta, lang, day):
        greg_date = day + datetime.timedelta(days=delta)
        hijri_date = Gregorian.fromdate(greg_date).to_hijri()
        hijri_date_words = f"{hijri_date.day} {hijri_date.month_name(language=lang)} {hijri_date.year}"
        greg_date_words = greg_date.strftime('%d %B %Y')
        date_dict = dict(greg_date=greg_date, greg_date_words=greg_date_words,
                         hijri_date=hijri_date.dmyformat(separator="-"),
                         hijri_date_words=hijri_date_words)
        return date_dict


class CreateNewContest(views.APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        return Response(gettext("post contest-name only"))

    def post(self, request, *args, **kwargs):
        contest_name = request.data.pop('contest-name')
        contest = Contest.objects.create(name=contest_name)
        username = util_methods.get_username_from_session(request)
        person = Person.objects.get(username=username)
        ContestPerson.objects.create(person=person, contest=contest, contest_role=3)
        return Response(gettext("contest created"))


class JoinContest(views.APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        return Response(gettext("post access-code only"))

    def post(self, request, *args, **kwargs):
        access_code = request.data.get('access-code', None)
        if not access_code:
            return Response(gettext("post access-code only"), status=400)
        contest = Contest.objects.filter(id__endswith=access_code.lower()).first()
        if contest:
            username = util_methods.get_username_from_session(request)
            person = Person.objects.get(username=username)
            try:
                ContestPerson.objects.create(person=person, contest=contest, contest_role=1)
                return Response(gettext("joined the new contest"))
            except IntegrityError:
                return Response(gettext("user already member in contest"), status=400)
        else:
            return Response(gettext("access code is not correct"), status=404)


class ResetPasswordView(views.APIView):
    def post(self, request, *args, **kwargs):
        validate_get_reset = kwargs["validate_get_reset"]
        if validate_get_reset == "get_token":
            return self.get_token(request)
        elif validate_get_reset == "validate_token":
            return self.validate_token(request)
        elif validate_get_reset == "reset_password":
            return self.reset_password(request)
        else:
            return Response(gettext("not found"), status=404)

    @staticmethod
    def validate_token(request):
        token = request.data.get('token', None)
        username = request.data.get('username', None)
        if not (username and token):
            return Response(gettext("post username and received token"), status=400)
        cached_username = cache.get(f"reset_password/{token}")
        if cached_username == username:
            return Response(gettext("valid token"))
        else:
            return Response(gettext("invalid token"), status=400)

    def reset_password(self, request):
        if self.validate_token(request).status_code == 200:
            token = request.data.get('token')
            password = request.data.get('password')
            cached_username = cache.get(f"reset_password/{token}")
            password = make_password(password)
            person = Person.objects.filter(username=cached_username).first()
            person.password = password
            person.save()
            return Response(gettext("password reset"))
        else:
            return Response(gettext("invalid token"), status=400)

    @staticmethod
    def get_token(request):
        username = request.data.get('username', None)
        if username:
            person = Person.objects.filter(username=username).first()
            if not person:
                return Response(gettext("user with this username was not found"), status=404)
        else:
            return Response(gettext("post username only"), status=400)

        subject = gettext('password reset subject')
        token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        cache.set(f"reset_password/{token}", username, 2 * 60 * 60)
        lang = get_language()
        context = {'token': token, "username": person.username}
        html_message = render_to_string(f'reset_password_{lang}.html', context)
        plain_message = render_to_string(f'reset_password_{lang}.txt', context)
        from_email = 'Wird App <no-reply@wird.app>'
        to_emails = [person.email]
        send_mail(subject, plain_message, from_email, to_emails, html_message=html_message)
        return Response(gettext("password reset success"))
