from django.contrib.auth.models import User, AbstractUser
from django.db import models

# Create your models here.
from superAdmin.models import Competition


class GeneralUser(AbstractUser):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, null=True)
