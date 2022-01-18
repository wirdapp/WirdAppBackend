from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.contrib.auth.models import User, Permission

from superAdmin.models import Competition, PointFormat


class CompAdmin(User):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    permissions = Permission()


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
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True)
    label = models.CharField(max_length=128, default='')
    description = models.CharField(max_length=256, default='')
    points_amount = models.IntegerField(default=0)
    upper_points_bound = models.IntegerField(default=1)
    form_type = models.ForeignKey(PointFormat, on_delete=models.CASCADE)


class CompGroup(models.Model):
    id = models.AutoField(primary_key=True)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    name = models.CharField(max_length=30, default='')
    admin = models.ForeignKey(CompAdmin, on_delete=models.SET_NULL, null=True)
    announcements = models.TextField(default="")
    extra_challenges = models.ForeignKey(PointTemplate, on_delete=models.CASCADE)

    def __str__(self):
        return '' if self.admin is None else self.admin.__str__()
