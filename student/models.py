from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from compAdmin.models import PointTemplate, CompGroup
from core.models import GeneralUser


def upload_location(instance, filename):
    filebase, extension = filename.split('.')
    return f'{instance.competition.id}/{instance.username}.{extension}'


class StudentUser(GeneralUser):
    profile_photo = models.ImageField(upload_to=upload_location, blank=True)
    read_only = models.BooleanField(default=False)
    group = models.ForeignKey(CompGroup, on_delete=models.CASCADE, related_name='group_students', null=True)

    def set_competition(self, competition):
        self.competition = competition

    class Meta:
        default_related_name = 'competition_students'
        ordering = ('first_name', 'last_name')


class PointRecord(models.Model):
    point_template = models.ForeignKey(PointTemplate, on_delete=models.CASCADE)
    student = models.ForeignKey(StudentUser, on_delete=models.CASCADE, null=True, related_name='student_points')
    point_scored_units = models.IntegerField(default=1)
    details = models.CharField(max_length=256, default='')
    ramadan_record_date = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(30)])
    point_total = models.IntegerField(default=1)

    def set_student(self, student):
        self.student = student

    def set_point_total(self, point_total):
        self.point_total = point_total

    class Meta:
        ordering = ('-ramadan_record_date',)
