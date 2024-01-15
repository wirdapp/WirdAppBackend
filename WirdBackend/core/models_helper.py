from admin_panel.models import ContestCriterion, Section, Group, ContestPersonGroup
from core import util_methods
from core.models import ContestPerson, Person, Contest


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
