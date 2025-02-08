from dal import autocomplete
from ditto.pinboard.admin import BookmarkAdmin
from ditto.pinboard.models import Bookmark
from django import forms
from django.contrib import admin
from django.urls import reverse_lazy

# So we can register our own LinkAdmin
admin.site.unregister(Bookmark)


# Overriding the BookmarkAdmin from django-ditto to customise it:
# - Mkae the Account field a hidden input
# - Make the tags use django-autocomplete-light
# - Move the post_time field into the collapsed section
# - Hide some of the read-only fields.


class LinkAdminForm(autocomplete.FutureModelForm):
    class Meta:
        model = Bookmark
        widgets = {
            # Hide the account field because there's only one of me:
            "account": forms.HiddenInput(),
            "tags": autocomplete.TaggitSelect2(
                url=reverse_lazy("pinboard:bookmark_tag_autocomplete")
            ),
        }
        fields = "__all__"


@admin.register(Bookmark)
class LinkAdmin(BookmarkAdmin):
    form = LinkAdminForm

    class Media:
        css = {"all": ("hines/css/admin.css",)}

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "account",
                    "url",
                    "title",
                    "description",
                    "tags",
                    ("is_private", "to_read"),
                )
            },
        ),
        (
            "Times",
            {
                "classes": ("collapse",),
                "fields": (
                    "post_time",
                    # "summary",
                    # "url_hash",
                    # "raw",
                    # "post_year_str",
                    # "fetch_time",
                    "time_created",
                    "time_modified",
                ),
            },
        ),
    )
