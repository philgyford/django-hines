from .base import *  # noqa: F403

DEBUG = False

ADMINS = [("Phil Gyford", "phil@gyford.com")]

MANAGERS = ADMINS

# If you *don't* want to prepend www to the URL, remove the setting from
# the environment entirely. Otherwise, set to 'True' (or anything tbh).
PREPEND_WWW = True


# Storing Media files on AWS.

DEFAULT_FILE_STORAGE = "hines.core.storages.CustomS3Boto3Storage"

AWS_ACCESS_KEY_ID = get_env_variable("AWS_ACCESS_KEY_ID")  # noqa: F405
AWS_SECRET_ACCESS_KEY = get_env_variable("AWS_SECRET_ACCESS_KEY")  # noqa: F405
AWS_STORAGE_BUCKET_NAME = get_env_variable("AWS_STORAGE_BUCKET_NAME")  # noqa: F405

AWS_QUERYSTRING_AUTH = False

AWS_DEFAULT_ACL = "public-read"

MEDIA_URL = "https://{}.s3.amazonaws.com{}".format(
    AWS_STORAGE_BUCKET_NAME, MEDIA_URL  # noqa: F405
)

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": get_env_variable("REDIS_URL"),  # noqa: F405
        "KEY_PREFIX": "hines",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # If Redis is down, ignore exceptions:
            "IGNORE_EXCEPTIONS": True,
        },
    }
}


# https
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS
# Applies to the ENTIRE domain... so maybe not?
# e.g. guardian.gyford.com, archive.gyford.com?
# SECURE_HSTS_SECONDS = 31536000 # 1 year
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True


# Sentry
# https://devcenter.heroku.com/articles/sentry#integrating-with-python-or-django
# via https://simonwillison.net/2017/Oct/17/free-continuous-deployment/

SENTRY_DSN = os.environ.get("SENTRY_DSN")  # noqa: F405

if SENTRY_DSN:
    INSTALLED_APPS += ("raven.contrib.django.raven_compat",)  # noqa: F405
    RAVEN_CONFIG = {
        "dsn": SENTRY_DSN,
        "release": os.environ.get("HEROKU_SLUG_COMMIT", ""),  # noqa: F405
    }


#############################################################################
# HINES-SPECIFIC SETTINGS.
