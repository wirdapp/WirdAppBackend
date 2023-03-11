import datetime

from django.utils.translation import get_language
from django.core.cache import cache
from django.db.models import Value, Sum, F
from django.db.models.functions import Concat
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
from core.permissions import IsContestMember
from core.serializers import *
from core.util_classes import MyModelViewSet
from member_panel.models import PointRecord


class ContestView(MyModelViewSet):
    serializer_class = ContestSerializer
    name = 'create-contest-view'
    member_allowed_methods = ['switch_contest', 'retrieve', 'list']
    admin_allowed_methods = ['switch_contest', 'retrieve', 'list']
    super_admin_allowed_methods = ['switch_contest', 'retrieve', 'list', 'update', 'partial_update']

    def get_queryset(self):
        username = util_methods.get_username_from_session(self.request)
        return models_helper.get_person_contests_queryset(username)

    @swagger_auto_schema(request_body=no_body,
                         responses={200: "contest switched successfully",
                                    404: "person is not enrolled in this contest"},
                         manual_parameters=[openapi.Parameter('contest_id', openapi.IN_QUERY,
                                                              description="uuid of the new contest",
                                                              type=openapi.TYPE_STRING)])
    @action(detail=False, methods=['post'])
    def switch_contest(self, request, *args, **kwargs):
        contests = self.get_queryset()
        new_contest = request.data["contest_id"]
        if contests.filter(contest__id=new_contest).exists():
            util_methods.update_current_contest_dict(request, new_contest)
            return Response(gettext("contest switched successfully"), status=status.HTTP_200_OK)
        else:
            return Response(gettext("person is not enrolled in this contest"), status=status.HTTP_404_NOT_FOUND)


class SignUpView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        user_type = self.request.query_params.get("type", "participant")
        if user_type == "participant":
            return ParticipantSignupSerializer
        elif user_type == "creator":
            return CreatorSignupSerializer

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('type', openapi.IN_QUERY, enum=['creator', 'participant'], type=openapi.TYPE_STRING)])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class CurrentContestPersonView(MyModelViewSet):
    serializer_class = PersonSerializer
    member_allowed_methods = ['retrieve', 'update', 'partial_update']
    admin_allowed_methods = []
    super_admin_allowed_methods = []

    def get_object(self):
        username = util_methods.get_username_from_session(self.request)
        return Person.objects.get(username=username)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        person = self.get_serializer(instance)
        current_contest = util_methods.get_current_contest_dict(self.request)
        data = dict(person=person.data, contest=current_contest)
        return Response(data)


class TopMembersOverall(views.APIView):
    permission_classes = [And(IsAuthenticated(), IsContestMember()), ]

    def get(self, request, *args, **kwargs):
        contest_id = util_methods.get_current_contest_dict(request)["id"]
        results = cache.get(contest_id)
        if not results:
            first_name = "person__person__first_name"
            last_name = "person__person__last_name"
            username = "person__person__username"
            results = PointRecord.objects.filter(person__contest__id=contest_id) \
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
            results = PointRecord.objects.filter(record_date=date, person__contest__id=contest_id) \
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
        for delta in range(-5, 3):  # 5 days before today and 3 days after
            greg_date = today + datetime.timedelta(days=delta)
            hijri_date = Gregorian.fromdate(greg_date).to_hijri()
            hijri_date_words = f"{hijri_date.day} {hijri_date.month_name(language=lang)} {hijri_date.year}"
            greg_date_words = greg_date.strftime('%d %B %Y')
            date_dict = dict(greg_date=greg_date.strftime("%d-%m-%Y"), greg_date_words=greg_date_words,
                             hijri_date=hijri_date.dmyformat(separator="-"),
                             hijri_date_words=hijri_date_words)
            results.append(date_dict)

        return Response(results)
