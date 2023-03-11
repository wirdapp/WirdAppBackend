import uuid

from django.contrib.auth.models import Permission
from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.utils.functional import cached_property

from core.models import Contest, ContestPerson


class Section(models.Model):
    label = models.CharField(default='', max_length=32)
    position = models.IntegerField(default=1)
    contest = models.ForeignKey(Contest, on_delete=models.PROTECT, related_name='contest_sections')

    def __str__(self):
        return self.label


class PointTemplate(models.Model):
    FORM_TYPES = (
        (1, 'Number'),
        (2, 'Check Box'),
        (3, 'Other'),
    )
    is_active = models.BooleanField(default=True)
    is_shown = models.BooleanField(default=True)
    order_in_section = models.IntegerField()
    custom_days = models.CharField(validators=[validate_comma_separated_integer_list], max_length=64, blank=True)
    contest = models.ForeignKey(Contest, on_delete=models.PROTECT, related_name="contest_point_templates")
    section = models.ForeignKey(Section, on_delete=models.PROTECT, related_name="contest_sections")

    label = models.CharField(max_length=128, default='')
    description = models.CharField(max_length=256, default='')
    form_type = models.PositiveSmallIntegerField(choices=FORM_TYPES, default=1)
    upper_units_bound = models.IntegerField(default=1)
    lower_units_bound = models.IntegerField(default=0)
    points_per_unit = models.IntegerField(default=1)

    class Meta:
        ordering = ('section__position', 'order_in_section')

    def __str__(self):
        return self.label


class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    announcements = models.TextField(default="", blank=True)
    contest = models.ForeignKey(Contest, on_delete=models.PROTECT)

    @cached_property
    def members_count(self):
        return ContestPerson.objects.filter(contest_role=1, group_role=1, group__id=self.id).count()

    def __str__(self):
        return self.name
