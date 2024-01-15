import uuid
from functools import cached_property
from gettext import gettext

from django.contrib.postgres import fields
from django.db import models
from polymorphic.models import PolymorphicModel
from psycopg2.extras import NumericRange

from core.models import Person, Contest, ContestPerson


class Section(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(default='', max_length=120)
    position = models.IntegerField()
    contest = models.ForeignKey("core.Contest", on_delete=models.PROTECT, related_name='contest_sections')

    def __str__(self):
        return f"{self.label} @ {self.contest.name}"


class ContestCriterion(PolymorphicModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=128)
    description = models.CharField(max_length=256)
    order_in_section = models.IntegerField()
    visible = models.BooleanField(default=True)
    activate_on_datetime = fields.ArrayField(fields.DateTimeRangeField(), blank=True, default=list)
    contest = models.ForeignKey("core.Contest", on_delete=models.PROTECT)
    section = models.ForeignKey(Section, on_delete=models.PROTECT)
    points = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.label} @ {self.contest.name}"


class NumberCriterion(ContestCriterion):
    lower_bound = models.IntegerField(default=0)
    upper_bound = models.IntegerField(default=20)


class CheckboxCriterion(ContestCriterion):
    checked_label = models.CharField(max_length=15, default="")
    unchecked_label = models.CharField(max_length=15, default="")


class MultiCheckboxCriterion(ContestCriterion):
    options = fields.HStoreField()
    partial_points = models.BooleanField(default=False)


class RadioCriterion(ContestCriterion):
    options = fields.HStoreField()


# None
class UserInputCriterion(ContestCriterion):
    allow_multiline = models.BooleanField(default=False)


class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, default='')
    announcements = fields.ArrayField(models.CharField(max_length=128, default="", blank=True), blank=True)
    contest = models.ForeignKey("core.Contest", on_delete=models.PROTECT)

    @cached_property
    def members_count(self):
        return ContestPersonGroup.objects.filter(group_role=1, group__id=self.id).count()

    @cached_property
    def admins_count(self):
        return ContestPersonGroup.objects.filter(group_role=2, group__id=self.id).count()

    def __str__(self):
        return f"{self.name} @ {self.contest.name}"


class ContestPersonGroup(models.Model):
    class GroupRole(models.IntegerChoices):
        ADMIN = (1, 'admin')
        MEMBER = (2, 'member')

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    contest_person = models.ForeignKey(ContestPerson, on_delete=models.PROTECT)
    group = models.ForeignKey(Group, on_delete=models.PROTECT)
    group_role = models.PositiveSmallIntegerField(choices=GroupRole.choices, default=GroupRole.MEMBER)

    def __str__(self):
        return f"{self.contest_person.person.username} @ {self.group.name} @ {self.contest_person.contest.name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["contest_person_id", 'group_id'],
                                    name="unique_group_person",
                                    violation_error_message=gettext("person is member of group")),
        ]
