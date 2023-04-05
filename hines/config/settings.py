"""
Should be extended by settings for specific environments.
"""
import os
from pathlib import Path

import dj_database_url
import sentry_sdk
from django.contrib import messages
from dotenv import load_dotenv
from sentry_sdk.integrations.django import DjangoIntegration

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Loads env variables from .env:
load_dotenv()


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

DEBUG = os.getenv("DEBUG", default="False") == "True"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS").split(",")


ADMINS = [("Phil Gyford", "phil@gyford.com")]

MANAGERS = ADMINS

# Application definition

INSTALLED_APPS = [
    # The dal apps must be before django.contrib.admin:
    "dal",
    "dal_select2",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.flatpages",
    "django.contrib.redirects",
    "django.contrib.sitemaps",
    "taggit",
    "django_comments",
    "django_q",
    "hcaptcha",
    "imagekit",
    "spectator.core",
    "spectator.events",
    "spectator.reading",
    "sortedm2m",
    "corsheaders",
    "mentions",
    "ditto.core",
    "ditto.flickr",
    "ditto.lastfm",
    "ditto.pinboard",
    "ditto.twitter",
    "hines.users",
    "hines.core",
    "hines.blocks",
    "hines.custom_comments",
    "hines.stats",
    "hines.links",
    "hines.patterns",
    "hines.up",
    "hines.weblogs",
]

MIDDLEWARE = [
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "mentions.middleware.WebmentionHeadMiddleware",
    "django.contrib.redirects.middleware.RedirectFallbackMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",
]

ROOT_URLCONF = "hines.config.urls"

default_template_loaders = [
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
]
cached_template_loaders = [
    ("django.template.loaders.cached.Loader", default_template_loaders),
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["hines/templates"],
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "hines.core.context_processors.core",
            ],
            # Stops templates being cached when DEBUG=True
            # https://nickjanetakis.com/blog/django-4-1-html-templates-are-cached-by-default-with-debug-true
            "loaders": default_template_loaders if DEBUG else cached_template_loaders,
        },
    },
]

WSGI_APPLICATION = "hines.config.wsgi.application"


DATABASES = {"default": dj_database_url.config(conn_max_age=500)}
DATABASES["default"]["OPTIONS"] = {"server_side_binding": True}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa: E501
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

# Using 'en-gb' caused the select2 included with autocomplete_light, that's
# used on admin screens for editing a Blog Post, to complain with:
#   ValueError: Missing staticfiles manifest entry for
#   'autocomplete_light/vendor/select2/dist/js/i18n/en-GB.js'
# (2018-01-05)
LANGUAGE_CODE = "en"

TIME_ZONE = "UTC"

USE_I18N = False

USE_TZ = True

USE_THOUSAND_SEPARATOR = True


STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

STATIC_ROOT = BASE_DIR / "hines" / "static_collected"

STATIC_URL = "/static/"

STATICFILES_DIRS = [BASE_DIR / "hines" / "static"]


MEDIA_ROOT = BASE_DIR / "hines" / "media"

MEDIA_URL = "/media/"


if os.getenv("HINES_USE_AWS_FOR_MEDIA", default="False") == "True":
    # Storing Media files on AWS.
    STORAGES["default"]["BACKEND"] = "hines.core.storages.CustomS3Boto3Storage"

    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")

    AWS_QUERYSTRING_AUTH = False

    AWS_DEFAULT_ACL = "public-read"

    MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com{MEDIA_URL}"


SITE_ID = 1

AUTH_USER_MODEL = "users.User"

# Monday:
FIRST_DAY_OF_WEEK = 1


# Use our custom CSS classes for message styles.
MESSAGE_TAGS = {
    messages.DEBUG: "utils-debug",
    messages.INFO: "utils-info",
    messages.SUCCESS: "utils-success",
    messages.WARNING: "utils-warning",
    messages.ERROR: "utils-error",
}


# Rwquired for Cloudflare Web Analytics:
SECURE_REFERRER_POLICY = "no-referrer-when-downgrade"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

#  Used when generating full URLs and the request object isn't available.
HINES_USE_HTTPS = os.getenv("HINES_USE_HTTPS", default="False") == "True"

if HINES_USE_HTTPS:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# Some tips: https://www.reddit.com/r/django/comments/x2h6cq/whats_your_logging_setup/
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "formatters": {
        "superverbose": {
            "format": "%(levelname)s %(asctime)s %(module)s:%(lineno)d %(process)d %(thread)d %(message)s"  # noqa: E501
        },
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s:%(lineno)d %(message)s"
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            # "filters": ["require_debug_true"],
            "formatter": "verbose",
        },
    },
    "loggers": {
        "commands": {
            # For management commands and tasks where we specify the "commands" logger
            "handlers": ["console"],
            "propagate": True,
            "level": os.getenv("HINES_LOG_LEVEL", default="INFO"),
        },
        "django": {
            "handlers": ["console"],
            "level": os.getenv("HINES_LOG_LEVEL", default="INFO"),
        },
    },
    # "root": {"handlers": ["console"], "level": "INFO"},
}


# Both of these are also used in HINES.apps.up.views.index:
HINES_CACHE_TYPE = os.getenv("HINES_CACHE_TYPE", default="dummy")
REDIS_URL = os.getenv("REDIS_URL", "")

# The DEFAULT_CACHE_TYPE setting is used in the /up/ URL to decide whether
# to check the state of the Redis cache or not

if HINES_CACHE_TYPE == "memory":
    # Use in-memory caching
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "HINES",
        }
    }

elif HINES_CACHE_TYPE == "redis" and REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": os.getenv("REDIS_URL"),
        }
    }

else:
    # Use dummy cache (ie, no caching)
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }


# Seconds before expiring a cached item. None for never expiring.
CACHES["default"]["TIMEOUT"] = 300

TEST_RUNNER = "hines.core.test_runner.HinesTestRunner"


if DEBUG:
    # Changes for local development

    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]

    INSTALLED_APPS += ["debug_toolbar", "django_extensions"]

    def show_toolbar(request):
        return True

    DEBUG_TOOLBAR_CONFIG = {
        "INTERCEPT_REDIRECTS": False,
        "SHOW_TOOLBAR_CALLBACK": show_toolbar,
    }

    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


########################################################################################
# THIRD-PARTY APP SETTINGS


# django-comments ######################################################

COMMENTS_APP = "hines.custom_comments"


# django-cors-headers ##################################################

CORS_ALLOWED_ORIGINS = [
    "http://www.gyford.test:8000",
    "https://www.gyford.com",
    "https://cloudflareinsights.com",
    "https://static.cloudflareinsights.com",
]

# django-hcaptcha ######################################################
# https://github.com/AndrejZbin/django-hcaptcha

# Used in the comments form.
HCAPTCHA_SITEKEY = os.getenv("HCAPTCHA_SITEKEY", default="")
HCAPTCHA_SECRET = os.getenv("HCAPTCHA_SECRET", default="")


# django-q2#############################################################

if os.getenv("DJANGOQ_REDIS_URL", ""):
    Q_CLUSTER = {
        "name": "hines",
        "label": "Django Q",
        # Number of seconds a worker can spend on a task before it's terminated:
        # Default None
        "timeout": 60,
        # Number of seconds to wait for a cluster to finish a task, before it’s
        # presented again. Must be bigger than timeout:
        # Default 60
        "retry": 120,
        # Number of tasks to process before recycling, releasing memory resources:
        # Default 500
        "recycle": 200,
        # Number of retry attempts for failed tasks. 0 for infinite retries:
        # Default 0 (infinite)
        "max_attempts": 3,
        # Should it execute missed timeslots from while cluster was down?
        # Default True
        "catch_up": False,
        "redis": os.getenv("DJANGOQ_REDIS_URL"),
    }


# django-imagekit ######################################################
# https://django-imagekit.readthedocs.io/en/stable/caching.html#removing-safeguards

IMAGEKIT_DEFAULT_CACHEFILE_STRATEGY = "imagekit.cachefiles.strategies.Optimistic"

# Need to specify this or in production it started using the local filesystem
# instead of S3BotoStorage:
IMAGEKIT_DEFAULT_FILE_STORAGE = STORAGES["default"]["BACKEND"]


# django-spectator #####################################################

HINES_MAPBOX_API_KEY = os.getenv("HINES_MAPBOX_API_KEY", default="")

if HINES_MAPBOX_API_KEY:
    SPECTATOR_MAPS = {
        "enable": True,
        "library": "mapbox",
        "tile_style": "mapbox://styles/mapbox/light-v10",
        "api_key": HINES_MAPBOX_API_KEY,
    }
else:
    SPECTATOR_MAPS = {"enable": False}


# django-taggit ########################################################

# We don't want to allow duplicate tags like 'Fish' and 'fish':
TAGGIT_CASE_INSENSITIVE = True


# django-wm ############################################################
# https://github.com/beatonma/django-wm/

WEBMENTIONS_USE_CELERY = False

WEBMENTIONS_AUTO_APPROVE = False

# So that we only save Webmentions to the pages of Posts:
WEBMENTIONS_INCOMING_TARGET_MODEL_REQUIRED = True

# Don't want to register the times we refer to our own pages:
WEBMENTIONS_ALLOW_SELF_MENTIONS = False

WEBMENTIONS_ALLOW_OUTGOING_DEFAULT = False

if HINES_USE_HTTPS:
    WEBMENTIONS_URL_SCHEME = "https"
else:
    WEBMENTIONS_URL_SCHEME = "http"

DOMAIN_NAME = os.getenv("WM_DOMAIN_NAME", default="")


# sentry-sdk ###########################################################

# Sentry
# https://devcenter.heroku.com/articles/sentry#integrating-with-python-or-django

SENTRY_DSN = os.getenv("SENTRY_DSN", default="")

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=0.01,
    )


# END THIRD-PARTY APP SETTINGS
########################################################################################


########################################################################################
# DJANGO-HINES-SPECIFIC SETTINGS


# ALSO see HINES_USE_HTTPS above.

# Most hines-related pages will be within this root directory:
# We override this in tests using an environment variable.
HINES_ROOT_DIR = os.getenv("HINES_ROOT_DIR", default="phil")

# Used in templates and the Everything RSS Feed, for things that don't
# have authors (so, not Blog Posts).
HINES_AUTHOR_NAME = "Phil Gyford"
HINES_AUTHOR_EMAIL = "phil@gyford.com"

# Location within the static directory of an image.
# Used for RSS feeds and Structured Data.
HINES_SITE_ICON = "hines/img/site_icon.jpg"

# Any Day Archive pages before this YYYY-MM-DD date will 404:
HINES_FIRST_DATE = "1989-06-02"

# If True, must also be True for a Blog's and a Post's allow_comments field
# before a comment on a Post is allowed.
HINES_COMMENTS_ALLOWED = os.getenv("HINES_COMMENTS_ALLOWED", default="True") == "True"

# Both these are used by Bleach to whitelist the contents of comments.
HINES_COMMENTS_ALLOWED_TAGS = {
    "a",
    "blockquote",
    "code",
    "strong",
    "em",
    "ul",
    "ol",
    "li",
    "pre",
}
HINES_COMMENTS_ALLOWED_ATTRIBUTES = {
    "a": ["href", "title"],
}

# Close comments on posts after this many days (assuming they're open):
# Or None to ignore this setting
HINES_COMMENTS_CLOSE_AFTER_DAYS = 30

# The slug to use for the RSS feed for submitted comments used by Admins:
HINES_COMMENTS_ADMIN_FEED_SLUG = os.getenv(
    "HINES_COMMENTS_ADMIN_FEED_SLUG", default="admin-comments"
)

# The slug to use for the RSS feed for webmentions used by Admins:
HINES_WEBMENTIONS_ADMIN_FEED_SLUG = os.getenv(
    "HINES_WEBMENTIONS_ADMIN_FEED_SLUG", default="admin-webmentions"
)

# Used to check submitted comments for spam using https://akismet.com:
HINES_AKISMET_API_KEY = os.getenv("HINES_AKISMET_API_KEY", default="")

# How many of each thing do we want displayed on the home page?
# The 'weblog_posts' uses the `slug` of each Blog to indicate how
# many posts of each to display.
HINES_HOME_PAGE_DISPLAY = {
    "flickr_photos": 4,
    "pinboard_bookmarks": 3,
    "weblog_posts": {"writing": 3, "comments": 1},
}

# Which blogs, accounts, etc should be featured in the 'everything combined' RSS feed?
HINES_EVERYTHING_FEED_KINDS = (
    ("blog_posts", "writing"),
    ("blog_posts", "comments"),
    ("flickr_photos", "35034346050@N01"),
    ("pinboard_bookmarks", "philgyford"),
)

# Describing different sets of templates that can be used for PostDetails
# between certain dates
#
# Any Post on the Blog with slug `writing` between the start/end dates will use the
# template at `weblogs/sets/<name>/post_detail.html`.
# Any other Post (e.g. the most recent) will use `weblogs/post_detail.html`.
#
# Set to None to have all Posts use `weblogs/post_detail.html` template.
HINES_TEMPLATE_SETS = (
    # Colourful:
    {"name": "2000", "start": "2000-03-01", "end": "2000-12-31"},
    # Monochrome:
    {"name": "2001", "start": "2001-01-01", "end": "2002-11-09"},
    # Similar, but blue links:
    {"name": "2002", "start": "2002-11-10", "end": "2006-03-15"},
    # Basis for the next decade+:
    {"name": "200603", "start": "2006-03-16", "end": "2006-08-29"},
    # Sight & Sound theme plus a few tweaks:
    {"name": "200608", "start": "2006-08-30", "end": "2009-02-09"},
    # Same but a bit wider and (later) responsive:
    {"name": "2009", "start": "2009-02-10", "end": "2018-01-04"},
)

# If set then the Cloudflare Web Analytics JavaScript will be put in every page:
HINES_CLOUDFLARE_ANALYTICS_TOKEN = os.getenv(
    "HINES_CLOUDFLARE_ANALYTICS_TOKEN", default=""
)


# Set to False to disable the hCaptcha field on the comment form:
HINES_USE_HCAPTCHA = True


# DATE/TIME FORMATS

# strftime to use for displaying dates in templates:
HINES_DATE_FORMAT = "%Y-%m-%d"

# strftime to use for displaying a month and year in templates:
HINES_DATE_YEAR_MONTH_FORMAT = "%b %Y"

# strftime to use for displaying times in templates:
HINES_TIME_FORMAT = "%H:%M"

# String to use when displaying a date AND a time in templates:
# [date] will be replaced with the date in HINES_DATE_FORMAT.
# [time] will be replaced with the time in HINES_TIME_FORMAT.
HINES_DATETIME_FORMAT = "[date] [time]"

# The date formats used by django-hines:
DITTO_CORE_DATE_FORMAT = HINES_DATE_FORMAT
DITTO_CORE_DATETIME_FORMAT = HINES_DATETIME_FORMAT

# The date format used by django-spectator:
SPECTATOR_DATE_FORMAT = HINES_DATE_FORMAT


# END DJANGO-HINES SPECIFIC SETTINGS
########################################################################################
