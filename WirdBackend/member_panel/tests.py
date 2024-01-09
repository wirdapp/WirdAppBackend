import datetime

from django.test import TestCase

from admin_panel.models import Section, NumberCriterion, MultiCheckboxCriterion, CheckboxCriterion
from core.models import Contest, Person, ContestPerson
from member_panel.models import CheckboxPointRecord
from member_panel.serializers import PointRecordSerializer, NumberPointRecordSerializer, CheckboxPointRecordSerializer


# Create your tests here.
class MyTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create(username='user', is_active=True)
        self.contest = Contest.objects.create(contest_id='contest',
                               name='contest',
                               readonly_mode=False,
                               start_date=datetime.date(2023, 10, 5),
                               end_date=datetime.date(2024, 12, 25))
        self.contest_person = ContestPerson.objects.create(person=self.person,
                                                           contest=self.contest,
                                                           contest_role=3)

        self.section = Section.objects.create(contest=self.contest, position=0)
        self.contest_criterion = NumberCriterion.objects.create(label='number',
                                                                description='number',
                                                                order_in_section=0,
                                                                section=self.section,
                                                                contest=self.contest,
                                                                points=3)

    def test_my_test(self):
        pr=NumberPointRecordSerializer(data={
            "contest_criterion": self.contest_criterion.id,
            "person": self.contest_person.uuid,
            "score": 2,
        }, context={'request': Context(data={'contest_id': self.contest.id})})


        print(pr.is_valid())
        print(pr.errors)


class MyTest2(TestCase):
    def setUp(self):
        self.person = Person.objects.create(username='user', is_active=True)
        self.contest = Contest.objects.create(contest_id='contest',
                                              name='contest',
                                              readonly_mode=False,
                                              start_date=datetime.date(2023, 10, 5),
                                              end_date=datetime.date(2024, 12, 25))
        self.contest_person = ContestPerson.objects.create(person=self.person,
                                                           contest=self.contest,
                                                           contest_role=3)

        self.section = Section.objects.create(contest=self.contest, position=0)
        self.contest_criterion = CheckboxCriterion.objects.create(
            label='number',
            description='number',
            order_in_section=0,
            section=self.section,
            contest=self.contest,
            points=3)
        print(self)

    def test_my_test(self):
        sr = CheckboxPointRecordSerializer(data={
            "contest_criterion": self.contest_criterion.id,
            "person": self.contest_person.uuid,
            "checked": True,
        }, context={'request': Context(data={'contest_id': self.contest.id})})
        sr.is_valid()
        try:
            sr.save()
        except Exception as e:
            print(e)
        x = CheckboxPointRecord.objects.all()

class Context:
    def __init__(self, data):
        self.COOKIES = data