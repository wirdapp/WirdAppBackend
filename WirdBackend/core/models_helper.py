from collections.abc import Iterable

from admin_panel.models import ContestCriterion, Section, Group, ContestPersonGroup
from core.models import ContestPerson, Contest, Person


def get_contest_people(contest_id, contest_role=(1, 2, 3)):
    return


def get_person_contests_ids_and_roles(username, contest_role=(0, 1, 2, 3, 4, 5)):
    queryset = ContestPerson.objects.filter(person__username=username, contest_role__in=contest_role) \
        .values_list("contest__id", "contest_role")

    return queryset


def get_person_contests_queryset(username, contest_role=(0, 1, 2, 3)):
    contest_ids = get_person_contests_ids_and_roles(username, contest_role)
    contest_ids = [c[0] for c in contest_ids]
    return Contest.objects.filter(id__in=contest_ids)


def get_person_managed_groups(username, current_contest):
    contest_id = current_contest["id"]
    role = current_contest["role"]
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
