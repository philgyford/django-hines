"""
Should be extended by settings for specific environments.
"""
from pathlib import Path

import environ
import sentry_sdk
from django.contrib import messages
from sentry_sdk.integrations.django import DjangoIntegration

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")


SECRET_KEY = env("DJANGO_SECRET_KEY")

DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")


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
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.flatpages",
    "django.contrib.redirects",
    "django.contrib.sitemaps",
    "taggit",
    "django_comments",
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
    "hines.weblogs",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Should go before WhiteNoiseMiddleware and CommonMiddleware:
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "mentions.middleware.WebmentionHeadMiddleware",
    # Can go at the end of the list:
    "django.contrib.redirects.middleware.RedirectFallbackMiddleware",
]

ROOT_URLCONF = "hines.config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["hines/templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "hines.core.context_processors.core",
            ],
        },
    },
]

WSGI_APPLICATION = "hines.config.wsgi.application"


# Uses DATABASE_URL environment variable:
DATABASES = {"default": env.db_url()}
DATABASES["default"]["CONN_MAX_AGE"] = 500


# Custom setting to enable the site-wide caching.
# (We must also have set up the CACHES setting, if making this True.)
USE_PER_SITE_CACHE = False

if USE_PER_SITE_CACHE:
    # Must be first:
    MIDDLEWARE = ["django.middleware.cache.UpdateCacheMiddleware"] + MIDDLEWARE
    # Must be last:
    MIDDLEWARE += [
        "django.middleware.cache.FetchFromCacheMiddleware",
    ]
    CACHE_MIDDLEWARE_ALIAS = "default"
    CACHE_MIDDLEWARE_SECONDS = 600
    CACHE_MIDDLEWARE_KEY_PREFIX = ""


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
# used on admin screens for editing a weblog Post, to complain with:
#   ValueError: Missing staticfiles manifest entry for
#   'autocomplete_light/vendor/select2/dist/js/i18n/en-GB.js'
# (2018-01-05)
LANGUAGE_CODE = "en"

TIME_ZONE = "UTC"

USE_I18N = False

USE_L10N = True

USE_TZ = True

USE_THOUSAND_SEPARATOR = True


STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

STATIC_ROOT = BASE_DIR / "hines" / "static_collected"

STATIC_URL = "/static/"

STATICFILES_DIRS = [BASE_DIR / "hines" / "static"]


MEDIA_ROOT = BASE_DIR / "hines" / "media"

MEDIA_URL = "/media/"


if env.bool("USE_AWS_FOR_MEDIA", False):
    # Storing Media files on AWS.
    DEFAULT_FILE_STORAGE = "hines.core.storages.CustomS3Boto3Storage"

    AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")

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


HINES_USE_HTTPS = env.bool("HINES_USE_HTTPS", default=False)

if HINES_USE_HTTPS:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "filters": {
#         "require_debug_false": {
#             "()": "django.utils.log.RequireDebugFalse",
#         },
#         "require_debug_true": {
#             "()": "django.utils.log.RequireDebugTrue",
#         },
#     },
#     "formatters": {
#         "rich": {"datefmt": "[%X]"},
#     },
#     "handlers": {
#         "console": {
#             "class": "rich.logging.RichHandler",
#             "filters": ["require_debug_true"],
#             "formatter": "rich",
#             "level": "INFO",
#             "rich_tracebacks": True,
#             "tracebacks_show_locals": True,
#         },
#     },
#     "loggers": {
#         "django": {
#             "handlers": [],
#             "level": env("HINES_LOG_LEVEL", default="ERROR"),
#         },
#     },
#     "root": {
#         "handlers": ["console"],
#         "level": env("HINES_LOG_LEVEL", default="ERROR"),
#     },
# }


HINES_CACHE = env("HINES_CACHE", default="memory")

if HINES_CACHE == "redis":
    # Use the TLS URL if set, otherwise, use the non-TLS one:
    REDIS_URL = env("REDIS_TLS_URL", default=env("REDIS_URL", default=""))
    if REDIS_URL != "":
        CACHES = {
            "default": {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": REDIS_URL,
                "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
            }
        }
        if env("REDIS_TLS_URL", default=""):
            CACHES["default"]["OPTIONS"]["CONNECTION_POOL_KWARGS"] = {
                "ssl_cert_reqs": None
            }

elif HINES_CACHE == "dummy":
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }


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


####################################################################
# THIRD-PARTY APPS


COMMENTS_APP = "hines.custom_comments"

# We don't want to allow duplicate tags like 'Fish' and 'fish':
TAGGIT_CASE_INSENSITIVE = True


# A directory of static files to be served in the root directory.
# e.g. 'robots.txt'.
WHITENOISE_ROOT = BASE_DIR / "hines" / "static_html"

# Visiting /example/ will serve /example/index.html:
WHITENOISE_INDEX_FILE = True

WHITENOISE_MIMETYPES = {".xsl": "text/xsl"}

HINES_MAPBOX_API_KEY = env("HINES_MAPBOX_API_KEY", default="")

if HINES_MAPBOX_API_KEY:
    SPECTATOR_MAPS = {
        "enable": True,
        "library": "mapbox",
        "tile_style": "mapbox://styles/mapbox/light-v10",
        "api_key": HINES_MAPBOX_API_KEY,
    }
else:
    SPECTATOR_MAPS = {"enable": False}


AWS_DEFAULT_ACL = None


# https://django-imagekit.readthedocs.io/en/stable/caching.html#removing-safeguards
IMAGEKIT_DEFAULT_CACHEFILE_STRATEGY = "imagekit.cachefiles.strategies.Optimistic"


CORS_ALLOWED_ORIGINS = [
    "http://www.gyford.local:8000",
    "https://www.gyford.com",
    "https://cloudflareinsights.com",
    "https://static.cloudflareinsights.com",
]


# Sentry
# https://devcenter.heroku.com/articles/sentry#integrating-with-python-or-django

SENTRY_DSN = env.bool("SENTRY_DSN", default="")

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
    )


# django-wm

WEBMENTIONS_USE_CELERY = False

WEBMENTIONS_AUTO_APPROVE = False

DOMAIN_NAME = env("WM_DOMAIN_NAME", default="")

# END THIRD-PARTY APPS
####################################################################


####################################################################
# DJANGO-HINES-SPECIFIC SETTINGS


# Most hines-related pages will be within this root directory:
# We only override this in settings by setting the environment variable.
HINES_ROOT_DIR = env("HINES_ROOT_DIR", default="phil")

# Used in templates and the Everything RSS Feed, for things that don't
# have authors (so, not Blog Posts).
HINES_AUTHOR_NAME = "Phil Gyford"
HINES_AUTHOR_EMAIL = "phil@gyford.com"

# Location within the static directory of an image.
# Used for RSS feeds and Structured Data.
HINES_SITE_ICON = "hines/img/site_icon.jpg"

# We won't show Day Archive pages before this YYYY-MM-DD date:
HINES_FIRST_DATE = "1989-06-02"

# If True, must also be True for a Blog's and a Post's allow_comments field
# before a comment on a Post is allowed.
HINES_COMMENTS_ALLOWED = True

# Both these are used by Bleach to whitelist the contents of comments.
HINES_COMMENTS_ALLOWED_TAGS = [
    "a",
    "blockquote",
    "code",
    "strong",
    "em",
    "ul",
    "ol",
    "li",
    "pre",
]
HINES_COMMENTS_ALLOWED_ATTRIBUTES = {
    "a": ["href", "title"],
}

# Close comments on posts after this many days (assuming they're open):
# Or None to ignore this setting
HINES_COMMENTS_CLOSE_AFTER_DAYS = 30

HINES_COMMENTS_ADMIN_FEED_SLUG = env(
    "HINES_COMMENTS_ADMIN_FEED_SLUG", default="admin-comments"
)

HINES_WEBMENTIONS_ADMIN_FEED_SLUG = env(
    "HINES_WEBMENTIONS_ADMIN_FEED_SLUG", default="admin-webmentions"
)


HINES_AKISMET_API_KEY = env("HINES_AKISMET_API_KEY", default="")

# How many of each thing do we want displayed on the home page?
HINES_HOME_PAGE_DISPLAY = {
    "flickr_photos": 4,
    "pinboard_bookmarks": 3,
    "weblog_posts": {"writing": 3, "comments": 1},
}

HINES_EVERYTHING_FEED_KINDS = (
    ("blog_posts", "writing"),
    ("blog_posts", "comments"),
    ("flickr_photos", "35034346050@N01"),
    ("pinboard_bookmarks", "philgyford"),
)

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

HINES_CLOUDFLARE_ANALYTICS_TOKEN = env("HINES_CLOUDFLARE_ANALYTICS_TOKEN", default="")

# Date/time formats

HINES_DATE_FORMAT = "%Y-%m-%d"
HINES_DATETIME_FORMAT = "[date] [time]"

DITTO_CORE_DATE_FORMAT = HINES_DATE_FORMAT
DITTO_CORE_DATETIME_FORMAT = HINES_DATETIME_FORMAT

SPECTATOR_DATE_FORMAT = HINES_DATE_FORMAT


# For https://github.com/AndrejZbin/django-hcaptcha
# Used in the comments form.
HCAPTCHA_SITEKEY = env("HCAPTCHA_SITEKEY", default="")
HCAPTCHA_SECRET = env("HCAPTCHA_SECRET", default="")

# Set to False to disable the hCaptcha field on the comment form:
HINES_USE_HCAPTCHA = True
