import datetime
from django.contrib.auth.hashers import make_password
from core.models import Contest, Person, ContestPerson


# Function to fill data in models
def create_contest(contest_id):
    contest_data = {
        'contest_id': contest_id,
        'name': contest_id.upper(),
        'description': 'Description for Contest',
        'show_standings': True,
        'readonly_mode': False,
        'start_date': datetime.date(2024, 1, 1),
        'end_date': datetime.date(2024, 1, 31),
    }
    contest = Contest.objects.create(**contest_data)

    owner_data = {
        'username': f'{contest_id}_contest_owner',
        "email": "test_mail@yahoo.com",
        "password": make_password("contest_owner"),
        'phone_number': '1111111111',
        "first_name": 'Owner Name',
        "last_name": 'Owner Surname'
    }
    owner = Person.objects.create(**owner_data)
    owner_contest_data = {
        'contest': contest,
        'person': owner,
        'contest_role': ContestPerson.ContestRole.CONTEST_OWNER,
    }
    ContestPerson.objects.create(**owner_contest_data)

    return contest, owner


def create_members(contest, count, role: ContestPerson.ContestRole):
    role_label = role.label
    members = []
    for i in range(count):
        member_data = {
            'username': f'{contest.contest_id}_{role_label}_{i}',
            "email": "test_mail@yahoo.com",
            "password": make_password(f'{contest.contest_id}_{role_label}_{i}'),
            'phone_number': f'555555555{i}',
            "first_name": f'{role_label}_{i} Name',
            "last_name": f'{role_label}_{i} Surname'
        }
        member = Person.objects.create(**member_data)
        member_contest_data = {
            'contest': contest,
            'person': member,
            'contest_role': role,
        }
        cp = ContestPerson.objects.create(**member_contest_data)
        members.append(cp)

    return members
