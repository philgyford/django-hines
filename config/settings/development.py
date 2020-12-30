from .base import *  # noqa: F403
from .base import get_env_variable

DEBUG = True

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# Storing Media files on AWS.

DEFAULT_FILE_STORAGE = "hines.core.storages.CustomS3Boto3Storage"

AWS_ACCESS_KEY_ID = get_env_variable("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = get_env_variable("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = get_env_variable("AWS_STORAGE_BUCKET_NAME")

AWS_QUERYSTRING_AUTH = False

MEDIA_URL = "https://{}.s3.amazonaws.com{}".format(
    AWS_STORAGE_BUCKET_NAME, MEDIA_URL  # noqa: F405
)  # noqa: F405


CACHES = {
    "default": {
        # Use i-memory caching:
        # "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        # Seconds before expiring a cached item. None for never expiring.
        # "TIMEOUT": 400,
        # Use django-redis:
        # "BACKEND": "django_redis.cache.RedisCache",
        # "LOCATION": get_env_variable("REDIS_URL"),
        # "KEY_PREFIX": "hines",
        # "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient",},
        # Use dummy cache (ie, no caching):
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# Globally enable/disable comments across the site.
# Overrides all other settings (close after days, per-post, etc).
HINES_COMMENTS_ALLOWED = True

# Close comments on posts after this many days (assuming they're open):
# Or None to ignore this setting
HINES_COMMENTS_CLOSE_AFTER_DAYS = None


# Debug Toolbar settings.
if DEBUG:
    MIDDLEWARE += [  # noqa: F405
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]
    INSTALLED_APPS += ["debug_toolbar", "django_extensions"]  # noqa: F405

    INTERNAL_IPS = ["127.0.0.1"]

    # Stop Django handling static files in favour of Whitenoise.
    # (When DEBUG = False)
    # Need to add the app just before staticfiles, so:
    new_apps = []
    for app in INSTALLED_APPS:
        if app == "django.contrib.staticfiles":
            new_apps.append("whitenoise.runserver_nostatic")
        new_apps.append(app)
    INSTALLED_APPS[:] = new_apps