from django.contrib.auth.models import User, AbstractUser
from django.db import models


# Create your models here.

class Competition(models.Model):
    id = models.CharField(max_length=30, primary_key=True, default='')
    name = models.CharField(max_length=30, default='')
    show_standings = models.BooleanField(default=True)
    announcements = models.TextField(default="", blank=True)
    readonly_mode = models.BooleanField(default=False, help_text='Stop scoring points and only show scored points')

    def __str__(self):
        return self.name


class GeneralUser(AbstractUser):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, null=True)

    def set_competition(self, competition):
        self.competition = competition

    class Meta:
        default_related_name = ''
