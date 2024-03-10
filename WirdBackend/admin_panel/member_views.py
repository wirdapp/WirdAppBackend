# views.py

from django.db.models import Sum, Count
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from admin_panel.member_serializers import AdminPolymorphicPointRecordSerializer
from core import util_methods, models_helper
from core.models import ContestPerson
from core.permissions import IsContestAdmin
from core.serializers import PersonSerializer
from core.util_classes import CustomPermissionsMixin
from member_panel.models import PointRecord


class Leaderboard(APIView):
    permission_classes = [IsContestAdmin]

    def get(self, request, *args, **kwargs):
        contest = util_methods.get_current_contest(request)
        limit = request.query_params.get("limit", None)
        person_info = ["person__" + i for i in ["username", "first_name", "last_name", "profile_photo"]]
        leaderboard = models_helper.get_leaderboard(contest).values("id", "total_points", *person_info)
        if limit:
            leaderboard = leaderboard[:int(limit)]
        return Response(leaderboard)


class ContestOverallResultsView(APIView):
    permission_classes = [IsContestAdmin]

    def get(self, request, *args, **kwargs):
        contest = util_methods.get_current_contest(request)
        start_date, end_date = util_methods.get_contest_and_request_related_start_and_end_date(request, contest)
        dates = util_methods.get_dates_between_two_dates(start_date, end_date)

        members = (ContestPerson.objects.filter(contest=contest, contest_role=ContestPerson.ContestRole.MEMBER)
                   .prefetch_related("contest_person_points", "person"))

        submission_counts = dict(PointRecord.objects.filter(person__in=members)
                                 .values('record_date').annotate(count=Count('id')).order_by('record_date')
                                 .values_list("record_date", "count"))

        aggregated_points = list(
            PointRecord.objects.filter(person__in=members)
            .values('record_date', "person__id", "person__person__first_name", "person__person__last_name")
            .annotate(total_points=Sum('point_total')).order_by('record_date', '-total_points')
        )

        results = []
        for i, date in enumerate(dates, start=1):
            top_by_day = []
            while aggregated_points and date == aggregated_points[0]["record_date"]:
                entry = aggregated_points.pop(0)
                top_by_day.append({
                    "id": entry["person__id"],
                    "first_name": entry["person__person__first_name"],
                    "last_name": entry["person__person__last_name"],
                    "points": entry["total_points"]
                })
            submission_count = submission_counts.get(date, 0)
            results.append(dict(date=date, submission_count=submission_count, top_three_by_day=top_by_day[:3]))

        return Response(results)


class UserResultsView(APIView):
    permission_classes = [IsContestAdmin]

    def get(self, request, *args, **kwargs):
        user_id = self.get_user_id(request, **kwargs)
        contest = util_methods.get_current_contest(request)
        contest_person = (ContestPerson.objects.filter(contest=contest, id=user_id)
                          .prefetch_related("contest_person_points").first())
        person_data = PersonSerializer(contest_person.person, fields=["username", "first_name", "last_name"]).data
        person_data.update({"id": contest_person.id})
        total_points = contest_person.contest_person_points.aggregate(total_points=Sum('point_total'))['total_points']
        scores = models_helper.get_person_points_by_criterion(contest_person).order_by("-point_total")
        start_date, end_date = util_methods.get_contest_and_request_related_start_and_end_date(request, contest)
        dates = util_methods.get_dates_between_two_dates(start_date, end_date)
        points_by_date = dict(models_helper.get_person_points_by_date(contest_person, dates, "-record_date")
                              .values_list('record_date', "points"))
        days = [{"index": i, "date": date.strftime("%Y-%m-%d"), "points": points_by_date.get(date, 0)}
                for i, date in enumerate(dates, start=1)]
        result = dict(person_data=person_data, total_points=total_points, days=days, scores=scores,
                      rank=models_helper.get_person_rank(contest_person))
        return Response(result)

    def get_user_id(self, request, **kwargs):
        return kwargs["user_id"]


class MemberPointRecordViewSet(CustomPermissionsMixin, viewsets.ModelViewSet):
    # super_admin_allowed_methods = ['list', 'retrieve', 'create', 'update', 'partial_update', 'destroy']
    permission_classes = [IsContestAdmin]
    # TODO: Admin is only allowed to edit points of his Group students
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
        context['record_date'] = self.kwargs.get("date")
        context['person'] = self.kwargs.get("user_id")
        return context
