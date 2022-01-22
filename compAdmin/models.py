from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.contrib.auth.models import Permission

from core.models import GeneralUser


class PointFormat(models.Model):
    id = models.CharField(max_length=64, default="", primary_key=True)
    label = models.CharField(max_length=64, default="")
    html = models.TextField(default="")


class Competition(models.Model):
    id = models.CharField(max_length=30, primary_key=True, default='')
    name = models.CharField(max_length=30, default='')
    admins = models.ManyToManyField('compAdmin.CompAdmin', related_name='comp_admins')
    show_standings = models.BooleanField(default=True)
    readonly_mode = models.BooleanField(default=False, help_text='Stop scoring points and only show scored points')

    def __str__(self):
        return self.name


class PointTemplate(models.Model):
    id = models.AutoField(primary_key=True)
    is_active = models.BooleanField(default=True)
    is_shown = models.BooleanField(default=True)
    order = models.IntegerField()
    custom_days = models.CharField(validators=[validate_comma_separated_integer_list], max_length=64)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, null=True)
    label = models.CharField(max_length=128, default='')
    description = models.CharField(max_length=256, default='')
    points_amount = models.IntegerField(default=0)
    upper_points_bound = models.IntegerField(default=1)
    form_type = models.ForeignKey(PointFormat, on_delete=models.CASCADE)

    def set_competition(self, competition):
        self.competition = competition


class Section(models.Model):
    id = models.CharField(primary_key=True, max_length=32)
    label = models.CharField(default='', max_length=32)
    position = models.IntegerField(default=1)
    section = models.ManyToManyField(PointTemplate, blank=True)

    def __str__(self):
        return self.label


class CompGroup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, default='')
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, null=True)
    announcements = models.TextField(default="", blank=True)
    extra_challenges = models.ManyToManyField(PointTemplate, blank=True)
    students = models.ManyToManyField('student.StudentUser', blank=True)

    def set_competition(self, competition):
        self.competition = competition


class CompAdmin(GeneralUser):
    permissions = models.CharField(validators=[validate_comma_separated_integer_list], max_length=9,
                                   default="0,0,0,0,0")
    managed_groups = models.ManyToManyField(CompGroup, blank=True, related_name="managed_groups")
    is_super_admin = models.BooleanField(default=False)
