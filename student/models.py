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
    #
    # @property
    # def total_points(self):
    #     return PointRecord.objects.prefetch_related('point_total_score').aggregate(models.Sum('point_total_score'))

    def set_competition(self, competition):
        self.competition = competition

    class Meta:
        default_related_name = 'competition_students'
        ordering = ('first_name', 'last_name')


class PointRecord(models.Model):
    point_template = models.ForeignKey(PointTemplate, on_delete=models.CASCADE)
    student = models.ForeignKey(StudentUser, on_delete=models.CASCADE, related_name='student_points')
    point_scored_units = models.IntegerField(default=1)
    details = models.CharField(max_length=256, default='')
    ramadan_record_date = models.IntegerField()

    @property
    def point_total_score(self):
        if self.point_template.lower_units_bound <= self.point_scored_units <= self.point_template.upper_units_bound:
            return self.point_scored_units * self.point_template.points_per_unit
        else:
            return 0

    class Meta:
        ordering = ('-ramadan_record_date',)
        # constraints = [
        #     models.CheckConstraint(
        #         check=models.Q(point_total_score=1) & models.Q(qt__lte=10),
        #         name="A qty value is valid between 1 and 10",
        #     )
        # ]
