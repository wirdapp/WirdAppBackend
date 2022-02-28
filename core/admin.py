from django.contrib import admin

# Register your models here.
from core.models import GeneralUser, Competition

admin.site.register(GeneralUser)
admin.site.register(Competition)
