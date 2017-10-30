"""
Should be extended by settings for specific environments.
"""
import os
from os import environ

from django.core.exceptions import ImproperlyConfigured


def get_env_variable(var_name):
    """Get the environment variable or raise exception."""
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = 'Set the {} environemnt variable.'.format(var_name)
        raise ImproperlyConfigured(error_msg)


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS_DIR = os.path.join(BASE_DIR, '..', 'hines')


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_variable('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    # The dal apps must be before django.contrib.admin:
    'dal',
    'dal_select2',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'django.contrib.redirects',

    'markdownx',
    'taggit',
    'django_comments',

    'spectator.core',
    'spectator.reading',

    'sortedm2m',
    'ditto.core',
    'ditto.flickr',
    'ditto.lastfm',
    'ditto.pinboard',
    'ditto.twitter',

    'hines.users',
    'hines.core',
    'hines.blocks',
    'hines.custom_comments',
    'hines.links',
    'hines.weblogs',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Can go at the end of the list:
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            'hines/templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'hines.core.context_processors.core',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

USE_THOUSAND_SEPARATOR = True



MEDIA_ROOT = os.path.join(APPS_DIR, 'media/')

MEDIA_URL = '/media/'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

STATIC_ROOT = os.path.join(APPS_DIR, 'static_collected/')

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(APPS_DIR, 'static'),
]


# A directory of static files to be served in the root directory.
# e.g. 'robots.txt'.
WHITENOISE_ROOT = os.path.join(APPS_DIR, 'static_html/')

# Visiting /example/ will serve /example/index.html:
WHITENOISE_INDEX_FILE = True


SITE_ID = 1

AUTH_USER_MODEL = 'users.User'

COMMENTS_APP = 'hines.custom_comments'

# We don't want to allow duplicate tags like 'Fish' and 'fish':
TAGGIT_CASE_INSENSITIVE = True

# Most hines-related pages will be within this root directory:
HINES_ROOT_DIR = 'phil'

# We won't show Date Archive pages before this YYYY-MM-DD date:
HINES_FIRST_DATE = '2000-03-15'

# Used to generate URLs when we don't have access to a request object:
HINES_USE_HTTPS = False

# If True, must also be True for a Blog's and a Post's allow_comments field
# before a comment on a Post is allowed.
HINES_ALLOW_COMMENTS = True

# Both these are used by Bleach to whitelist the contents of comments.
HINES_COMMENTS_ALLOWED_TAGS = [
   'a', 'blockquote', 'code', 'strong', 'em', 'ul', 'ol', 'li', 'pre',
]
HINES_COMMENTS_ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title',],
}

MT_MYSQL_DB_HOST = os.environ.get('MT_MYSQL_DB_HOST', None)
MT_MYSQL_DB_USER = os.environ.get('MT_MYSQL_DB_USER', None)
MT_MYSQL_DB_PASSWORD = os.environ.get('MT_MYSQL_DB_PASSWORD', None)
MT_MYSQL_DB_NAME = os.environ.get('MT_MYSQL_DB_NAME', None)
MT_MYSQL_DB_PORT = os.environ.get('MT_MYSQL_DB_PORT', None)

