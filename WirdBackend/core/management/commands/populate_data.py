import datetime

from django.core.management.base import BaseCommand
from ._populate_core_data import create_contest, create_members
from ._populate_admin_data import populate_contest_criteria
from core.models import ContestPerson
from ._populate_point_records import fill_point_records
import random


class Command(BaseCommand):
    help = 'Populate data into Django models'

    def handle(self, *args, **options):
        # Your existing fill_data function
        def fill_data():
            contest1, contest_1_owner = create_contest("contest_1")
            contest2, contest_2_owner = create_contest("contest_2")
            contest1_super_admins = create_members(contest1, 2, ContestPerson.ContestRole.SUPER_ADMIN)
            contest1_admins = create_members(contest1, 3, ContestPerson.ContestRole.ADMIN)
            contest1_members = create_members(contest1, 3, ContestPerson.ContestRole.MEMBER)
            contest1_pending = create_members(contest1, 3, ContestPerson.ContestRole.PENDING_MEMBER)

            contest2_super_admins = create_members(contest2, 2, ContestPerson.ContestRole.SUPER_ADMIN)
            contest2_admins = create_members(contest2, 3, ContestPerson.ContestRole.ADMIN)
            contest2_members = create_members(contest2, 3, ContestPerson.ContestRole.MEMBER)
            contest2_pending = create_members(contest2, 3, ContestPerson.ContestRole.PENDING_MEMBER)

            contest1_criteria_dict = populate_contest_criteria(contest1)
            contest2_criteria_dict = populate_contest_criteria(contest2)

            chosen_date = []
            for i in range(100):
                person = random.choice(contest1_members)
                date = datetime.date(2024, 1, random.randint(1, 23)).strftime('%Y-%m-%d')
                if (date, person) in chosen_date:
                    continue
                else:
                    fill_point_records(person, date, contest1_criteria_dict)
                    chosen_date.append((date, person))

            for i in range(100):
                person = random.choice(contest2_members)
                date = datetime.date(2024, 1, random.randint(1, 23)).strftime('%Y-%m-%d')
                if (date, person) in chosen_date:
                    continue
                else:
                    fill_point_records(person, date, contest2_criteria_dict)
                    chosen_date.append((date, person))

        # Call the function to fill data
        fill_data()

        self.stdout.write(self.style.SUCCESS('Data populated successfully!'))
