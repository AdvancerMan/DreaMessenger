from django.contrib import admin

from messenger import models

admin.site.register(models.Dialogue)
admin.site.register(models.Message)
admin.site.register(models.Picture)
admin.site.register(models.PictureV2)
