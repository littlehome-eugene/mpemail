from django.contrib import admin
from mpemail.models.email import Email


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    pass
