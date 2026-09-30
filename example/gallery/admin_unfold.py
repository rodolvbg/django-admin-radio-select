"""The demo's admin on an Unfold site (see ``example.settings_unfold``)."""

from unfold.admin import ModelAdmin, StackedInline, TabularInline
from unfold.sites import UnfoldAdminSite

from django_admin_radio_select import ExclusiveRadioFieldsMixin

from .models import Album, AlbumStacked, Image

site = UnfoldAdminSite(name="admin")


class ImageTabularInline(ExclusiveRadioFieldsMixin, TabularInline):
    model = Image
    extra = 3
    radio_select_exclusive_fields = ("is_primary", "is_featured")


class ImageStackedInline(ExclusiveRadioFieldsMixin, StackedInline):
    model = Image
    extra = 3
    radio_select_exclusive_fields = ("is_primary", "is_featured")


class AlbumAdmin(ExclusiveRadioFieldsMixin, ModelAdmin):
    inlines = [ImageTabularInline]
    list_display = ("title", "is_featured")
    list_editable = ("is_featured",)
    radio_select_exclusive_fields = ("is_featured",)


class AlbumStackedAdmin(ModelAdmin):
    inlines = [ImageStackedInline]


site.register(Album, AlbumAdmin)
site.register(AlbumStacked, AlbumStackedAdmin)
