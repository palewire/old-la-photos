from django.contrib import admin
from photos.models import Photo, Face


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ("title", "tweeted", "faces_extracted", "subcollection")
    list_filter = ("subcollection",)
    search_fields = ("title",)


@admin.register(Face)
class FaceAdmin(admin.ModelAdmin):
    list_display = ("id", "photo")
