from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.Search)
admin.site.register(models.Midi)
admin.site.register(models.SheetMusic)