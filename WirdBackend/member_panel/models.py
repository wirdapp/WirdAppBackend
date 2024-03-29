import datetime
import uuid

from django.db import models
from django.contrib.postgres import fields
from polymorphic.models import PolymorphicModel
from admin_panel.models import ContestCriterion
from core.models import ContestPerson


def NON_POLYMORPHIC_CASCADE(collector, field, sub_objs, using):
    return models.CASCADE(collector, field, sub_objs.non_polymorphic(), using)


class PointRecord(PolymorphicModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey(ContestPerson, on_delete=NON_POLYMORPHIC_CASCADE, related_name='contest_person_points')
    contest_criterion = models.ForeignKey(ContestCriterion, on_delete=NON_POLYMORPHIC_CASCADE)
    record_date = models.DateField()
    timestamp = models.DateTimeField(auto_now=True)
    point_total = models.IntegerField(default=0)

    class Meta:
        ordering = ('-record_date',)
        unique_together = ('person', 'contest_criterion', 'record_date')

    def __str__(self):
        return f'{self.person.id}:{self.contest_criterion.label}:date:{self.record_date}'


class NumberPointRecord(PointRecord):
    number = models.IntegerField(default=0)


class CheckboxPointRecord(PointRecord):
    checked = models.BooleanField(False)


class MultiCheckboxPointRecord(PointRecord):
    choices = fields.ArrayField(models.CharField(max_length=200), default=list, blank=True)


class RadioPointRecord(PointRecord):
    choice = models.CharField(max_length=200, default="")


class UserInputPointRecord(PointRecord):
    user_input = models.TextField(default="", max_length=1024)
    reviewed_by_admin = models.BooleanField(default=False)
