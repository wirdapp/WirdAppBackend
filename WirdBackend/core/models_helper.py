from django.db.models import Sum

from admin_panel.models import Group, ContestPersonGroup
from core import util_methods
from core.models import ContestPerson


def get_person_contests(username, contest_role=(0, 1, 2, 3, 4)):
    contest_persons = (ContestPerson.objects.filter(person__username=username, contest_role__in=contest_role)
                       .prefetch_related("contest"))
    return [contest_person.contest for contest_person in contest_persons]


def get_current_user_managed_groups(request):
    contest = util_methods.get_current_contest(request)
    role = util_methods.get_current_user_contest_role(request)
    username = util_methods.get_username(request)
    if role <= ContestPerson.ContestRole.SUPER_ADMIN.value:
        return Group.objects.filter(contest=contest)
    elif role == ContestPerson.ContestRole.ADMIN.value:
        contest_person_groups = (ContestPersonGroup.objects
                                 .prefetch_related('group')
                                 .filter(person__username=username,
                                         group__contest=contest, group_role=1))
        return [cpg.groups for cpg in contest_person_groups]

    else:
        return Group.objects.none()


def get_person_points_by_date(contest_person, dates, order_by):
    return (contest_person.contest_person_points
            .filter(record_date__in=dates)
            .values('record_date')
            .annotate(points=Sum('point_total'))
            .order_by(order_by)
            .values_list('record_date', "points"))


def get_person_points_by_criterion(contest_person):
    return (contest_person.contest_person_points.values("contest_criterion__id")
            .annotate(point_total=Sum("point_total"))
            .order_by("point_total")
            .values('contest_criterion__id', 'contest_criterion__label', 'point_total'))


def get_leaderboard(contest):
    return (ContestPerson.objects
            .filter(contest=contest, contest_role=ContestPerson.ContestRole.MEMBER)
            .annotate(total_points=Sum('contest_person_points__point_total'))
            .filter(total_points__gt=0)
            .order_by("-total_points")
            .values("id", "person__username", "person__first_name", "person__last_name"
                    , "person__profile_photo", "total_points"))
