from dal import autocomplete

from django import forms
from django.contrib import admin
from django.urls import reverse_lazy

from hines.core.utils import datetime_now
from .models import Blog, Post, Trackback


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "short_name",
        "allow_comments",
        "show_author_email_in_feed",
        "sort_order",
    )
    search_fields = ("name", "short_name")

    fieldsets = (
        (
            None,
            {"fields": ("name", "short_name", "slug", "sort_order", "allow_comments")},
        ),
        (
            "Feed",
            {"fields": ("feed_title", "feed_description", "show_author_email_in_feed")},
        ),
        (
            "Times",
            {"classes": ("collapse",), "fields": ("time_created", "time_modified")},
        ),
    )

    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("time_created", "time_modified")


class PostAdminForm(autocomplete.FutureModelForm):
    """
    So we can add custom validation and autocomplete for tags, and tweak
    formatting of other inputs.
    """

    class Meta:
        model = Post
        widgets = {
            "title": forms.TextInput(attrs={"class": "vLargeTextField"}),
            "intro": forms.Textarea(attrs={"class": "vLargeTextField", "rows": 6}),
            "body": forms.Textarea(
                attrs={"class": "vLargeTextField js-patterns", "rows": 20}
            ),
            "excerpt": forms.Textarea(attrs={"class": "vLargeTextField", "rows": 3}),
            # The django-autocomplete-light tag widget:
            "tags": autocomplete.TaggitSelect2(
                url=reverse_lazy("weblogs:post_tag_autocomplete")
            ),
        }
        fields = "__all__"

    def clean(self):
        """
        A Post that's Scheduled should have a time_published that's in the future.
        """
        status = self.cleaned_data.get("status")
        time_published = self.cleaned_data.get("time_published")

        if status == Post.Status.SCHEDULED:
            if time_published is None:
                raise forms.ValidationError(
                    "If this post is Scheduled it should have a Time Published."
                )
            elif time_published <= datetime_now():
                raise forms.ValidationError(
                    "This post is Scheduled but its Time Published is in the past."
                )
        return self.cleaned_data


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "blog",
        "title",
        "status_icon",
        "allow_comments",
        "comment_count",
        "allow_incoming_webmentions",
        "allow_outgoing_webmentions",
        "time_published",
        # 'is_featured',
    )
    list_display_links = ("title",)
    list_filter = ("blog", "time_published", "status", "featured")
    search_fields = ("title", "excerpt", "intro", "body")
    date_hierarchy = "time_published"

    form = PostAdminForm

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "blog",
                    "title",
                    "slug",
                    "status",
                    "time_published",
                    (
                        "allow_comments",
                        "allow_incoming_webmentions",
                        "allow_outgoing_webmentions",
                    ),
                )
            },
        ),
        ("The post", {"fields": ("html_format", "intro", "body", "excerpt", "tags")}),
        (
            "Extra",
            {"classes": ("collapse",), "fields": ("author", "featured", "remote_url")},
        ),
        (
            "Comments",
            {
                "classes": ("collapse",),
                "fields": (
                    "comment_count",
                    "last_comment_time",
                    "trackback_count",
                ),
            },
        ),
        (
            "Times",
            {"classes": ("collapse",), "fields": ("time_created", "time_modified")},
        ),
    )

    prepopulated_fields = {"slug": ("title",)}
    radio_fields = {"featured": admin.HORIZONTAL}
    readonly_fields = ("time_created", "time_modified")

    class Media:
        css = {"all": ("hines/css/vendor/easymde.min.css", "hines/css/admin.css")}
        js = ("hines/js/vendor/easymde.min.js", "hines/js/admin.min.js")

    def status_icon(self, obj):
        if obj.status == Post.Status.LIVE:
            return "✅"
        elif obj.status == Post.Status.DRAFT:
            return "…"
        elif obj.status == Post.Status.SCHEDULED:
            return "🕙"
        else:
            return ""

    status_icon.short_description = "Status"

    def is_featured(self, obj):
        return obj.featured == Post.FeaturedChoices.IS_FEATURED

    is_featured.boolean = True
    is_featured.short_description = "Featured?"


@admin.register(Trackback)
class TrackbackAdmin(admin.ModelAdmin):
    list_display = ("title", "blog_name", "post", "time_created", "is_visible")
    list_display_links = ("title",)
    search_fields = ("title", "excerpt")
    date_hierarchy = "time_created"

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "post",
                    "blog_name",
                    "title",
                    "excerpt",
                    "url",
                    "ip_address",
                    "is_visible",
                )
            },
        ),
        (
            "Times",
            {"classes": ("collapse",), "fields": ("time_created", "time_modified")},
        ),
    )

    raw_id_fields = ("post",)
    readonly_fields = ("time_created", "time_modified")
