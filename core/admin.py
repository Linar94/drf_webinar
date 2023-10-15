from django.contrib import admin

from core.models import Group


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("id", "slug", "title")
