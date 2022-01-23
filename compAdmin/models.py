import time

from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.contrib.auth.models import Permission
from datetime import timedelta

from django.utils import timezone

from core.models import GeneralUser


# Django automatically creates reverse relationships for foreign keys.
# This means that if you have a model1 object, you can get its related model2 object,
# even if you only defined the foreign key in the model2 object:
# Example:
# model1.objects.get(pk=1).model2_set.all()  # Fetch me all model2 for this model1

class Competition(models.Model):
    id = models.CharField(max_length=30, primary_key=True, default='')
    name = models.CharField(max_length=30, default='')
    show_standings = models.BooleanField(default=True)
    readonly_mode = models.BooleanField(default=False, help_text='Stop scoring points and only show scored points')

    def __str__(self):
        return self.name


class PointFormat(models.Model):
    id = models.CharField(max_length=64, default="", primary_key=True)
    label = models.CharField(max_length=64, default="")
    html = models.TextField(default="")


class Section(models.Model):
    id = models.CharField(primary_key=True, max_length=32)
    label = models.CharField(default='', max_length=32)
    position = models.IntegerField(default=1)

    def __str__(self):
        return self.label


class PointTemplate(models.Model):
    id = models.AutoField(primary_key=True)
    is_active = models.BooleanField(default=True)
    is_shown = models.BooleanField(default=True)
    order = models.IntegerField()
    custom_days = models.CharField(validators=[validate_comma_separated_integer_list], max_length=64)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, null=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True)

    label = models.CharField(max_length=128, default='')
    description = models.CharField(max_length=256, default='')
    form_type = models.ForeignKey(PointFormat, on_delete=models.CASCADE)
    upper_units_bound = models.IntegerField(default=1)
    lower_units_bound = models.IntegerField(default=0)
    points_per_unit = models.IntegerField(default=1)

    def set_competition(self, competition):
        self.competition = competition


class ExtraChallengeTemplate(PointTemplate):
    is_for_all = models.BooleanField(default=False)
    is_temporary = models.BooleanField(default=False)
    time_frame = models.DurationField(default=timedelta(days=1))
    date_posted = models.DateTimeField(default=timezone.now)


class UserInputPointTemplate(ExtraChallengeTemplate):
    # used for exams and other points with user input
    pass


class CompAdmin(GeneralUser):
    permissions = models.CharField(validators=[validate_comma_separated_integer_list], max_length=9,
                                   default="0,0,0,0,0")
    is_super_admin = models.BooleanField(default=False)


class CompGroup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, default='')
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, null=True, related_name='competition_groups')
    announcements = models.TextField(default="", blank=True)
    extra_challenges = models.ManyToManyField(ExtraChallengeTemplate, blank=True)
    admin = models.ForeignKey(CompAdmin, on_delete=models.SET_NULL, null=True, related_name='managed_groups')

    def set_competition(self, competition):
        self.competition = competition
