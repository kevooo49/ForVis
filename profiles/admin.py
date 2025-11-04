from django.contrib import admin

from profiles.models import Profile, TextFile, JsonFile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(TextFile)
class TextFileAdmin(admin.ModelAdmin):
    pass


@admin.register(JsonFile)
class JsonFileAdmin(admin.ModelAdmin):
    pass
