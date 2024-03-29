import datetime
from gettext import gettext

from rest_framework import views
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from admin_panel import member_views as admin_member_views
from admin_panel.models import ContestCriterion, Section
from admin_panel.serializers import ContestPolymorphicCriterionSerializer, SectionSerializer
from core import util_methods, models_helper
from core.models import ContestPerson
from core.permissions import IsContestMember
from core.serializers import ContestSerializer
from core.util_classes import CustomPermissionsMixin, BulkCreateModelMixin, BulkUpdateModelMixin
from core.util_methods import get_current_contest_person
from member_panel.models import PointRecord
from member_panel.serializers import PolymorphicPointRecordSerializer


class MemberPointRecordViewSet(CustomPermissionsMixin, BulkCreateModelMixin, BulkUpdateModelMixin,
                               viewsets.ModelViewSet):
    member_allowed_methods = ['list', 'retrieve', 'create', 'update', 'partial_update', 'destroy', 'bulk_update']
    serializer_class = PolymorphicPointRecordSerializer

    def get_queryset(self):
        person = get_current_contest_person(self.request)
        date = self.kwargs.get("date")
        return PointRecord.objects.filter(person__id=person.id, record_date=date)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['record_date'] = self.kwargs["date"]
        context['person'] = util_methods.get_current_contest_person(self.request).id
        return context

    @action(detail=False, methods=['patch', 'put'])
    def bulk_update(self, request, *args, **kwargs):
        if request.method == "PATCH":
            kwargs["partial"] = True
        return super().bulk_update(request, *args, **kwargs)


class ContestCriteriaViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ContestPolymorphicCriterionSerializer
    permission_classes = [IsContestMember]

    def get_queryset(self):
        contest = util_methods.get_current_contest(self.request)
        return ContestCriterion.objects.filter(contest=contest).order_by('section__position', "order_in_section")


class ContestSectionsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SectionSerializer
    permission_classes = [IsContestMember]

    def get_queryset(self):
        contest = util_methods.get_current_contest(self.request)
        return Section.objects.filter(contest=contest)


class UserResultsView(admin_member_views.UserResultsView):
    permission_classes = [IsContestMember]

    def get_user_id(self, request, **kwargs):
        return util_methods.get_current_contest_person(request).id


class Leaderboard(admin_member_views.Leaderboard):
    permission_classes = [IsContestMember]

    def get(self, request, *args, **kwargs):
        contest = util_methods.get_current_contest(request)
        if contest.show_standings:
            return super(Leaderboard, self).get(request, *args, **kwargs)
        else:
            return Response(gettext("leaderboard is not available now"), 403)


class AnnouncementsView(views.APIView):
    permission_classes = [IsContestMember]

    def get(self, request, *args, **kwargs):
        contest = util_methods.get_current_contest(request)
        results = []
        contest_announcements = contest.announcements
        for announcement in contest_announcements:
            announcement.update({"source": "contest"})
            results.append(announcement)
        groups = models_helper.get_person_enrolled_groups(request).values("name", 'announcements')
        for group in list(groups):
            [ann.update(source=group["name"]) for ann in group["announcements"]]
            results.extend(group["announcements"])
        return Response(results)


class HomePageView(views.APIView):
    permission_classes = [IsContestMember]

    # TODO: Delete this after this year
    def get(self, request, *args, **kwargs):
        result = {}
        contest = util_methods.get_current_contest(request)
        contest_person = util_methods.get_current_contest_person(request)
        result["contest"] = ContestSerializer(contest, fields=["name", "contest_photo", "start_date", "end_date"]).data
        result["participant"] = ContestPerson.objects.filter(contest=contest).count()
        person_info = ["person__" + i for i in ["username", "first_name", "last_name", "profile_photo"]]
        result["leaderboard"] = (models_helper.get_leaderboard(contest)[:3].values(*person_info, "total_points"))
        today = datetime.datetime.today()
        yesterday = today - datetime.timedelta(days=1)
        result["points"] = (models_helper.get_person_points_by_date(contest_person, [yesterday, today], "-record_date")
                            .values('record_date', "points"))
        result["rank"] = models_helper.get_person_rank(contest_person)
        return Response(result)
