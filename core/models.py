from django.contrib.auth.models import User, AbstractUser
from django.db import models


# Create your models here.
class GeneralUser(AbstractUser):
    competition = models.ForeignKey('compAdmin.Competition', on_delete=models.CASCADE, null=True)

    def set_competition(self, competition):
        self.competition = competition
