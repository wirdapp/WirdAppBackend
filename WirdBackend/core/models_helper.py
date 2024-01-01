from admin_panel.models import ContestCriterion, Section, Group, ContestPersonGroup
from core import util_methods
from core.models import ContestPerson, Person, Contest


def get_contest_person_objects(username, contest_role=(0, 1, 2, 3, 4)):
    return ContestPerson.objects.filter(person__username=username, contest_role__in=contest_role)


def get_person_contests(username, contest_role=(0, 1, 2, 3, 4)):
    person_contests = get_contest_person_objects(username, contest_role).values_list('contest', flat=True)
    contests = Contest.objects.filter(id__in=person_contests)
    return contests


def get_current_user_managed_groups(request):
    contest_id = util_methods.get_current_contest_id(request)
    role = util_methods.get_current_user_contest_role(request)
    username = util_methods.get_username(request)
    if role <= ContestPerson.ContestRole.SUPER_ADMIN.value:
        return Group.objects.filter(contest__id=contest_id)
    elif role == ContestPerson.ContestRole.ADMIN.value:
        return (ContestPersonGroup.objects
                .filter(person__username=username, group__contest__id=contest_id, group_role=1)
                .values("group"))
    else:
        return Group.objects.none()


def get_group_admins_person_objects(group_id):
    person_ids = ContestPersonGroup.objects.filter(group__id=group_id, group_role=2) \
        .values_list('contest_person__person__id', flat=True)
    return Person.objects.filter(id__in=person_ids)


def get_group_members_contest_person_ids(group_id):
    return ContestPersonGroup.objects.filter(group__id=group_id, group_role=1) \
        .values_list('contest_person_id', flat=True)


def get_group_members_person_objects(group_id):
    person_ids = ContestPersonGroup.objects.filter(group__id=group_id, group_role=1) \
        .values_list('contest_person__person__id', flat=True)
    return Person.objects.filter(id__in=person_ids)


def get_contest_point_templates(contest_id):
    return ContestCriterion.objects.filter(contest__id=contest_id)


def get_contest_sections(contest_id):
    return Section.objects.filter(contest__id=contest_id)


def get_contest_groups(contest_id):
    return Group.objects.filter(contest__id=contest_id)
