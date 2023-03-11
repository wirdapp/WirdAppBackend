from django.contrib import admin

# Register your models here.
from core.models import *

admin.site.register(Person)
admin.site.register(Contest)
admin.site.register(ContestPerson)
admin.site.register(Group)
admin.site.register(ContestPersonGroups)
