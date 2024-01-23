import datetime

from django.core.management.base import BaseCommand
from ._populate_core_data import create_contest, create_members
from ._populate_admin_data import populate_contest_criteria
from core.models import *
from admin_panel.models import *
from member_panel.models import *
from ._populate_point_records import fill_point_records
import random


class Command(BaseCommand):
    help = 'Populate data into Django models'

    def handle(self, *args, **options):
        # Your existing fill_data function
        def erase_data():
            UserInputPointRecord.objects.all().delete()
            NumberPointRecord.objects.all().delete()
            CheckboxPointRecord.objects.all().delete()
            MultiCheckboxPointRecord.objects.all().delete()
            RadioPointRecord.objects.all().delete()
            PointRecord.objects.all().delete()

            UserInputCriterion.objects.all().delete()
            NumberCriterion.objects.all().delete()
            CheckboxCriterion.objects.all().delete()
            MultiCheckboxCriterion.objects.all().delete()
            RadioCriterion.objects.all().delete()
            ContestCriterion.objects.all().delete()
            ContestPersonGroup.objects.all().delete()
            ContestPerson.objects.all().delete()
            Person.objects.all().delete()

            Group.objects.all().delete()
            Section.objects.all().delete()
            Contest.objects.all().delete()


        # Call the function to fill data
        erase_data()

        self.stdout.write(self.style.SUCCESS('Data erased successfully!'))
