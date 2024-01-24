# views.py
import datetime

from django.db.models import Sum, Value, Count
from django.db.models.functions import Concat
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from admin_panel.member_serializers import AdminPolymorphicPointRecordSerializer
from core import util_methods
from core.models import ContestPerson
from core.permissions import IsContestAdmin
from core.serializers import PersonSerializer
from core.util_classes import CustomPermissionsMixin
from core.util_methods import get_dates_between_two_dates
from member_panel.models import PointRecord


class Leaderboard(APIView):
    permission_classes = [IsContestAdmin]

    def get(self, request, *args, **kwargs):
        contest = util_methods.get_current_contest(request)
        contest_persons = (ContestPerson.objects
                           .filter(contest=contest, contest_role=ContestPerson.ContestRole.MEMBER)
                           .annotate(total_points=Sum('contest_person_points__point_total'))
                           .filter(total_points__gt=0)
                           .order_by("-total_points")
                           .prefetch_related("person", 'contest_person_points'))

        members = []

        for i, contest_person in enumerate(contest_persons, start=1):
            person_data = PersonSerializer(contest_person.person,
                                           fields=["username", "first_name", "last_name", "profile_photo"]).data
            person_data.update({"id": contest_person.id})

            member_data = dict(rank=i, person_data=person_data, total_points=contest_person.total_points)
            members.append(member_data)

        return Response({"members": members})


class ContestOverallResultsView(APIView):
    def get(self, request, *args, **kwargs):
        contest = util_methods.get_current_contest(request)
        dates = get_dates_between_two_dates(contest.start_date, min(contest.end_date, datetime.date.today()))
        members = (ContestPerson.objects.filter(contest=contest, contest_role=ContestPerson.ContestRole.MEMBER)
                   .prefetch_related("contest_person_points", "person"))

        submission_counts = dict(PointRecord.objects.filter(person__in=members)
                                 .values('record_date').annotate(count=Count('id')).order_by('record_date')
                                 .values_list("record_date", "count"))

        aggregated_points = list(
            PointRecord.objects.filter(person__in=members).values('record_date', "person")
            .annotate(person_full_name=Concat('person__person__first_name', Value(' '), 'person__person__last_name'))
            .annotate(total_points=Sum('point_total')).order_by('record_date', '-total_points')
        )

        results = []
        for i, date in enumerate(dates, start=1):
            count = 0
            top_three_by_day = []
            while aggregated_points and date == aggregated_points[0]["record_date"] and count < 3:
                entry = aggregated_points.pop(0)
                top_three_by_day.append(
                    dict(id=entry["person_full_name"], name=entry["person_full_name"], points=entry["total_points"])
                )
                count += 1

            submission_count = submission_counts.get(date, 0)
            results.append(dict(date=date, submission_count=submission_count, top_three_by_day=top_three_by_day))

        return Response(results)


class UserResultsView(APIView):
    permission_classes = [IsContestAdmin]

    def get_user_id(self, request, **kwargs):
        return kwargs["user_id"]

    @staticmethod
    def get_points_by_date(contest_person, dates):
        points_by_date = dict(contest_person.contest_person_points
                              .values('record_date')
                              .annotate(points=Sum('point_total'))
                              .order_by('-record_date')
                              .values_list('record_date', "points"))

        scores = [{"index": j, "date": date.strftime("%Y-%m-%d"),
                   "points": points_by_date.get(date, 0)}
                  for j, date in enumerate(dates, start=1)]
        return scores

    def get(self, request, *args, **kwargs):
        user_id = self.get_user_id(request, **kwargs)
        contest = util_methods.get_current_contest(request)
        contest_person = (ContestPerson.objects.filter(contest=contest, id=user_id)
                          .prefetch_related("contest_person_points").first())
        person_data = PersonSerializer(contest_person.person, fields=["username", "first_name", "last_name"]).data
        person_data.update({"id": contest_person.id})
        total_points = contest_person.contest_person_points.aggregate(total_points=Sum('point_total'))['total_points']
        scores = (contest_person.contest_person_points.values("contest_criterion__id")
                  .annotate(point_total=Sum("point_total"))
                  .values('contest_criterion__id', 'contest_criterion__label', 'point_total'))
        dates = get_dates_between_two_dates(contest.start_date, min(datetime.date.today(), contest.end_date))
        days = self.get_points_by_date(contest_person, dates)
        result = dict(person_data=person_data, total_points=total_points, days=days, scores=scores)
        return Response(result)


class MemberPointRecordViewSet(CustomPermissionsMixin, viewsets.ModelViewSet):
    super_admin_allowed_methods = ['list', 'retrieve', 'create', 'update', 'partial_update', 'destroy']
    serializer_class = AdminPolymorphicPointRecordSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        total_points = queryset.aggregate(total_points=Sum('point_total'))["total_points"]
        return Response({"total_points": total_points, "points": serializer.data})

    def get_queryset(self):
        contest = util_methods.get_current_contest(request=self.request)
        user_id = self.kwargs.get("user_id")
        date = self.kwargs.get("date")
        return ContestPerson.objects.get(contest=contest, id=user_id).contest_person_points.filter(record_date=date)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        contest = util_methods.get_current_contest(request=self.request)
        user_id = self.kwargs.get("user_id")
        date = self.kwargs.get("date")
        context['date'] = date
        context['user_id'] = ContestPerson.objects.get(contest=contest, id=user_id)
        return context
