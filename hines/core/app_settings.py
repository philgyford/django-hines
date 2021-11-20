from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


COMMENTS_ALLOWED = getattr(settings, "HINES_COMMENTS_ALLOWED", True)

COMMENTS_ALLOWED_TAGS = getattr(
    settings,
    "HINES_COMMENTS_ALLOWED_TAGS",
    [
        "a",
        "abbr",
        "acronym",
        "b",
        "blockquote",
        "code",
        "em",
        "i",
        "li",
        "ol",
        "strong",
        "ul",
    ],
)

COMMENTS_ALLOWED_ATTRIBUTES = getattr(
    settings,
    "HINES_COMMENTS_ALLOWED_ATTRIBUTES",
    {"a": ["href", "title"], "acronym": ["title"], "abbr": ["title"]},
)


COMMENTS_CLOSE_AFTER_DAYS = getattr(settings, "HINES_COMMENTS_CLOSE_AFTER_DAYS", None)

if COMMENTS_CLOSE_AFTER_DAYS is not None and not isinstance(
    COMMENTS_CLOSE_AFTER_DAYS, int
):
    raise ImproperlyConfigured(
        "The HINES_COMMENTS_CLOSE_AFTER_DAYS setting should be an integer, "
        f"but it's 'f{COMMENTS_CLOSE_AFTER_DAYS}"
    )

COMMENTS_ADMIN_FEED_SLUG = getattr(
    settings,
    "HINES_COMMENTS_ADMIN_FEED_SLUG",
    "admin-comments",
)

AKISMET_API_KEY = getattr(settings, "HINES_AKISMET_API_KEY", None)

AUTHOR_NAME = getattr(settings, "HINES_AUTHOR_NAME", "")

AUTHOR_EMAIL = getattr(settings, "HINES_AUTHOR_EMAIL", "")

SITE_ICON = getattr(settings, "HINES_SITE_ICON", "")

DATE_FORMAT = getattr(settings, "HINES_DATE_FORMAT", "%-d %b %Y")

DATE_YEAR_MONTH_FORMAT = getattr(settings, "HINES_DATE_YEAR_MONTH_FORMAT", "%b %Y")

DATETIME_FORMAT = getattr(settings, "HINES_DATETIME_FORMAT", "[time] on [date]")

FIRST_DATE = getattr(settings, "HINES_FIRST_DATE", False)

CLOUDFLARE_ANALYTICS_TOKEN = getattr(settings, "HINES_CLOUDFLARE_ANALYTICS_TOKEN", "")

HOME_PAGE_DISPLAY = getattr(settings, "HINES_HOME_PAGE_DISPLAY", {})

EVERYTHING_FEED_KINDS = getattr(settings, "HINES_EVERYTHING_FEED_KINDS", ())

ROOT_DIR = getattr(settings, "HINES_ROOT_DIR", "")

TEMPLATE_SETS = getattr(settings, "HINES_TEMPLATE_SETS", None)

TIME_FORMAT = getattr(settings, "HIENS_TIME_FORMAT", "%H:%M")

USE_HTTPS = getattr(settings, "HINES_USE_HTTPS", False)
