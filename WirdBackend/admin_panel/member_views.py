# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum

from core import util_methods
from core.models import ContestPerson
from core.permissions import IsContestAdmin
from core.serializers import PersonSerializer


class Leaderboard(APIView):
    permission_classes = [IsContestAdmin]

    def get(self, request, *args, **kwargs):
        contest = util_methods.get_current_contest(request)
        contest_persons = (ContestPerson.objects.filter(contest=contest)
                           .prefetch_related('contest_person_points'))

        result = {'members': []}

        for contest_person in contest_persons:
            person_data = PersonSerializer(contest_person.person,
                                           fields=["id", "first_name", "last_name", "profile_picture"])
            total_points = (contest_person.contest_person_points
                            .aggregate(total_points=Sum('point_total'))['total_points'] or 0)

            member_data = dict(personal_data=person_data.data, total_point=total_points, scores=[])

            points_by_date = (contest_person.contest_person_points.values('record_date')
                              .annotate(points=Sum('point_total')).order_by('-record_date'))

            member_data["scores"] = points_by_date
            result['members'].append(member_data)

        result = sorted(result, key=lambda x: x[total_points], reverse=True)

        return Response(result)
