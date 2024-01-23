# views.py
import datetime

from django.db.models import Count
from django.db.models import Sum
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
        dates = get_dates_between_two_dates(contest.start_date, min(datetime.date.today(), contest.end_date))

        for i, contest_person in enumerate(contest_persons, start=1):
            person_data = PersonSerializer(contest_person.person,
                                           fields=["username", "first_name", "last_name", "profile_photo"]).data
            person_data.update({"id": contest_person.id})

            scores = get_points_by_date(contest_person, dates)

            member_data = dict(rank=i, person_data=person_data, total_points=contest_person.total_points, scores=scores)
            members.append(member_data)

        return Response({"members": members})


class ContestResultsView(APIView):
    permission_classes = [IsContestAdmin]

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id", None)
        if user_id:
            return self.get_user_results(user_id, request)
        else:
            return self.get_overall_results(request)

    def get_overall_results(self, request):
        #
        contest = util_methods.get_current_contest(request)
        dates = get_dates_between_two_dates(contest.start_date, min(datetime.date.today(), contest.end_date))
        members = (ContestPerson.objects.filter(contest=contest, contest_role=ContestPerson.ContestRole.MEMBER)
                   .prefetch_related("contest_person_points"))
        submission_counts = dict(PointRecord.objects.filter(person__in=members)
                                 .values('record_date').annotate(count=Count('id')).order_by('record_date')
                                 .values_list("record_date", "count"))

        aggregated_points = list(PointRecord.objects.filter(person__in=members).values('record_date', 'person')
                                 .annotate(total_points=Sum('point_total')).order_by('record_date', '-total_points'))
        # TODO: Top Three Per Day
        results = []
        for i, date in enumerate(dates, start=1):
            results.append({""})
            submission_count = submission_counts[date]
            results.append(dict(date=date, submission_count=submission_count))

        return Response(results)

    def get_user_results(self, user_id, request):
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
        days = get_points_by_date(contest_person, dates)
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
