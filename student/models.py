from django.db import models

from compAdmin.models import PointTemplate
from core.models import GeneralUser


class PointRecord(models.Model):
    type = models.ForeignKey(PointTemplate, on_delete=models.CASCADE)
    total_amount = models.IntegerField()
    details = models.CharField(max_length=256, default='')
    ramadan_record_date = models.IntegerField()

    class Meta:
        ordering = ('-ramadan_record_date',)


class StudentUser(GeneralUser):
    points = models.ManyToManyField(PointRecord, blank=True)
    read_only = models.BooleanField(default=False)

    @property
    def total_points(self):
        return self.points.objects.aggregate(models.Sum('price'))

    def set_competition(self, competition):
        self.competition = competition

    class Meta:
        ordering = ('first_name', 'last_name')
