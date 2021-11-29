from urllib.parse import urlparse

from django.contrib import admin

from .models import IncomingWebmention, OutgoingWebmention


@admin.register(IncomingWebmention)
class IncomingWebmentionAdmin(admin.ModelAdmin):
    list_display = ("source_title", "is_public", "is_validated")

    search_fields = ("source_title", "source_url", "target_url")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "content_type",
                    "object_pk",
                    "source_title",
                    "source_url",
                    "target_url",
                    "is_public",
                    "is_validated",
                    "source_is_deleted",
                )
            },
        ),
        (
            "Times",
            {"classes": ("collapse",), "fields": ("time_created", "time_modified")},
        ),
    )

    readonly_fields = ("time_created", "time_modified")


@admin.register(OutgoingWebmention)
class OutgoingWebmentionAdmin(admin.ModelAdmin):
    list_display = (
        "truncated_source_url",
        "truncated_target_url",
        "status_icon",
        "last_attempt_time",
    )
    list_filter = ("status",)

    search_fields = ("source_url", "target_url", "endpoint_url")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "content_type",
                    "object_pk",
                    "status",
                    "source_url",
                    "target_url",
                    "target_endpoint_url",
                    "target_response_code",
                    "endpoint_response_code",
                    "error_message",
                    "last_attempt_time",
                )
            },
        ),
        (
            "Times",
            {"classes": ("collapse",), "fields": ("time_created", "time_modified")},
        ),
    )

    readonly_fields = ("time_created", "time_modified")

    @admin.display(description="Source URL")
    def truncated_source_url(self, obj):
        if obj.source_url:
            u = urlparse(obj.source_url)
            return f"{u.path}{u.query}"
        else:
            return "—"

    @admin.display(description="Target URL")
    def truncated_target_url(self, obj):
        return _remove_scheme_from_url(obj.target_url)

    @admin.display(description="Status")
    def status_icon(self, obj):
        if obj.status == OutgoingWebmention.Status.WAITING:
            return "🕙"
        elif obj.status == OutgoingWebmention.Status.OK:
            return "✅"
        elif obj.status in OutgoingWebmention.get_error_statuses():
            return "❗️"
        else:
            return ""


def _remove_scheme_from_url(url):
    "Returns a URL without the 'https://'"
    s = "—"

    if url:
        u = urlparse(url)
        s = f"{u.netloc}{u.path}"
        if u.query:
            s += f"?{u.query}"
        if u.fragment:
            s += f"#{u.fragment}"

    return s
