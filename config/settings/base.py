"""
Should be extended by settings for specific environments.
"""
import os

import dj_database_url

from django.core.exceptions import ImproperlyConfigured


def get_env_variable(var_name):
    """Get the environment variable or raise exception."""
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the {} environemnt variable.".format(var_name)
        raise ImproperlyConfigured(error_msg)


# Most hines-related pages will be within this root directory:
HINES_ROOT_DIR = "phil"


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS_DIR = os.path.join(BASE_DIR, "..", "hines")


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_variable("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = get_env_variable("ALLOWED_HOSTS").split(",")


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
    "imagekit",
    "spectator.core",
    "spectator.events",
    "spectator.reading",
    "sortedm2m",
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
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Can go at the end of the list:
    "django.contrib.redirects.middleware.RedirectFallbackMiddleware",
]

ROOT_URLCONF = "config.urls"

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

WSGI_APPLICATION = "config.wsgi.application"


# Uses DATABASE_URL environment variable:
DATABASES = {"default": dj_database_url.config()}
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


# I think this is only used if we're NOT using S3:
MEDIA_ROOT = os.path.join(APPS_DIR, "media")
MEDIA_URL = "/{}/".format(HINES_ROOT_DIR)

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

STATIC_ROOT = os.path.join(APPS_DIR, "static_collected/")

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    os.path.join(APPS_DIR, "static"),
]


SITE_ID = 1

AUTH_USER_MODEL = "users.User"

# Monday:
FIRST_DAY_OF_WEEK = 1


####################################################################
# THIRD-PARTY APPS


COMMENTS_APP = "hines.custom_comments"

# We don't want to allow duplicate tags like 'Fish' and 'fish':
TAGGIT_CASE_INSENSITIVE = True


# A directory of static files to be served in the root directory.
# e.g. 'robots.txt'.
WHITENOISE_ROOT = os.path.join(APPS_DIR, "static_html/")

# Visiting /example/ will serve /example/index.html:
WHITENOISE_INDEX_FILE = True


try:
    SPECTATOR_MAPS = {
        "enable": True,
        "library": "mapbox",
        "tile_style": "mapbox://styles/mapbox/light-v10",
        "api_key": get_env_variable("HINES_MAPBOX_API_KEY"),
    }
except ImproperlyConfigured:
    SPECTATOR_MAPS = {"enable": False}


AWS_DEFAULT_ACL = None


# END THIRD-PARTY APPS
####################################################################


####################################################################
# DJANGO-HINES-SPECIFIC SETTINGS

# Also see HINES_ROOT_DIR at top of file.

# Used in templates and the Everything RSS Feed, for things that don't
# have authors (so, not Blog Posts).
HINES_AUTHOR_NAME = "Phil Gyford"
HINES_AUTHOR_EMAIL = "phil@gyford.com"

# Location within the static directory of an image.
# Used for RSS feeds and Structured Data.
HINES_SITE_ICON = "hines/img/site_icon.jpg"

# We won't show Day Archive pages before this YYYY-MM-DD date:
HINES_FIRST_DATE = "1989-06-02"

# Used to generate URLs when we don't have access to a request object:
HINES_USE_HTTPS = False

# If True, must also be True for a Blog's and a Post's allow_comments field
# before a comment on a Post is allowed.
HINES_ALLOW_COMMENTS = True

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

HINES_GOOGLE_ANALYTICS_ID = os.environ.get("HINES_GOOGLE_ANALYTICS_ID", None)

# Date/time formats

HINES_DATE_FORMAT = "%Y-%m-%d"
HINES_DATETIME_FORMAT = "[date] [time]"

DITTO_CORE_DATE_FORMAT = HINES_DATE_FORMAT
DITTO_CORE_DATETIME_FORMAT = HINES_DATETIME_FORMAT

SPECTATOR_DATE_FORMAT = HINES_DATE_FORMAT
