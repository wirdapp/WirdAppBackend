import uuid

from django.contrib.postgres import fields
from django.core.validators import MinValueValidator
from django.db import models
from polymorphic.models import PolymorphicModel


class Section(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(default='', max_length=32)
    position = models.IntegerField(default=1)
    contest = models.ForeignKey("core.Contest", on_delete=models.PROTECT, related_name='contest_sections')

    def __str__(self):
        return self.label


class PointTemplate(PolymorphicModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_in_section = models.IntegerField()
    is_active = models.BooleanField(default=True)
    is_shown = models.BooleanField(default=True)
    custom_days = fields.ArrayField(models.DateField(), blank=True, default=[])  # Only available for postgresSQL
    contest = models.ForeignKey("core.Contest", on_delete=models.PROTECT, related_name="contest_point_templates")
    section = models.ForeignKey(Section, on_delete=models.PROTECT)

    label = models.CharField(max_length=128, default='')
    description = models.CharField(max_length=256, default='')

    class Meta:
        ordering = ('section__position', 'order_in_section')

    def __str__(self):
        return self.label

    @property
    def template_type(self):
        return self.__class__.__name__


class NumberPointTemplate(PointTemplate):
    upper_units_bound = models.IntegerField(default=5)
    lower_units_bound = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    points_per_unit = models.IntegerField(default=1, validators=[MinValueValidator(1)])


class CheckboxPointTemplate(PointTemplate):
    points_if_done = models.PositiveIntegerField(default=1)
