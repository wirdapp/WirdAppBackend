from django.core.validators import validate_comma_separated_integer_list
from django.db import models


class Section(models.Model):
    label = models.CharField(default='', max_length=32)
    position = models.IntegerField(default=1)
    contest = models.ForeignKey("core.Contest", on_delete=models.PROTECT, related_name='contest_sections')

    def __str__(self):
        return self.label


class PointTemplate(models.Model):
    class FormType(models.IntegerChoices):
        NUM = (1, 'Number')
        CHECKBOX = (2, 'Check Box')
        OTHER = (3, 'Other')

    is_active = models.BooleanField(default=True)
    is_shown = models.BooleanField(default=True)
    order_in_section = models.IntegerField()
    custom_days = models.CharField(validators=[validate_comma_separated_integer_list], max_length=64, blank=True)
    contest = models.ForeignKey("core.Contest", on_delete=models.PROTECT, related_name="contest_point_templates")
    section = models.ForeignKey(Section, on_delete=models.PROTECT, related_name="contest_sections")

    label = models.CharField(max_length=128, default='')
    description = models.CharField(max_length=256, default='')
    form_type = models.PositiveSmallIntegerField(choices=FormType.choices, default=FormType.NUM)
    upper_units_bound = models.IntegerField(default=1)
    lower_units_bound = models.IntegerField(default=0)
    points_per_unit = models.IntegerField(default=1)

    class Meta:
        ordering = ('section__position', 'order_in_section')

    def __str__(self):
        return self.label
