from django.contrib import admin

# Register your models here.
from core.models import Person, Contest

admin.site.register(Person)
admin.site.register(Contest)
