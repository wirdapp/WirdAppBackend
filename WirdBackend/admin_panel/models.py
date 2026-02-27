import uuid
from functools import cached_property
from gettext import gettext

from django.contrib.postgres import fields
from django.db import models
from polymorphic.models import PolymorphicModel

from core.models import Person, Contest, ContestPerson


class Section(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(default='', max_length=120)
    position = models.IntegerField()
    contest = models.ForeignKey("core.Contest", on_delete=models.CASCADE, related_name='contest_sections')

    def __str__(self):
        return f"{self.label} @ {self.contest.name}"


class ContestCriterion(PolymorphicModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=128)
    description = models.CharField(max_length=256)
    order_in_section = models.IntegerField()
    visible = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    activate_on_dates = fields.ArrayField(models.DateField(), blank=True, default=list)
    deactivate_on_dates = fields.ArrayField(models.DateField(), blank=True, default=list)
    contest = models.ForeignKey("core.Contest", on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    points = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.label} @ {self.contest.name}"

    @cached_property
    def maximum_possible_points(self):
        return self.points


class NumberCriterion(ContestCriterion):
    lower_bound = models.IntegerField(default=0)
    upper_bound = models.IntegerField(default=20)

    @cached_property
    def maximum_possible_points(self):
        return self.points * self.upper_bound


class CheckboxCriterion(ContestCriterion):
    checked_label = models.CharField(max_length=15, default="")
    unchecked_label = models.CharField(max_length=15, default="")


class MultiCheckboxCriterion(ContestCriterion):
    options = models.JSONField()
    partial_points = models.BooleanField(default=False)

    @cached_property
    def maximum_possible_points(self):
        if self.partial_points:
            return sum(op["is_correct"] for op in self.options) * self.points
        else:
            return self.points


class RadioCriterion(ContestCriterion):
    options = models.JSONField()


# None
class UserInputCriterion(ContestCriterion):
    allow_multiline = models.BooleanField(default=False)


class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, default='')
    announcements = models.JSONField(default=dict)
    contest = models.ForeignKey("core.Contest", on_delete=models.CASCADE)

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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    contest_person = models.ForeignKey(ContestPerson, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    group_role = models.PositiveSmallIntegerField(choices=GroupRole.choices, default=GroupRole.MEMBER)

    def __str__(self):
        return f"{self.contest_person.person.username} @ {self.group.name} @ {self.contest_person.contest.name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["contest_person_id", 'group_id'],
                                    name="unique_group_person",
                                    violation_error_message=gettext("person is member of group")),
        ]


class ExportJob(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    contest = models.ForeignKey("core.Contest", on_delete=models.CASCADE, related_name='export_jobs')
    requester = models.ForeignKey(ContestPerson, on_delete=models.CASCADE, related_name='export_jobs')

    # Date filters
    start_date = models.DateField()
    end_date = models.DateField()

    # Member selection (mutually exclusive)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    member_ids = models.JSONField(null=True, blank=True, help_text="List of ContestPerson UUIDs")
    all_members = models.BooleanField(default=False, help_text="Export all contest members")

    # Result
    serialized_data = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    error_message = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"ExportJob {self.id} [{self.status}] by {self.requester}"
