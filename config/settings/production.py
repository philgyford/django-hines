from base import *
import dj_database_url


DEBUG = False

ADMINS = [
    ('Phil Gyford', 'phil@gyford.com'),
]

MANAGERS = ADMINS

# Uses DATABASE_URL environment variable:
DATABASES = {'default': dj_database_url.config()}
DATABASES['default']['CONN_MAX_AGE'] = 500

# If you *don't* want to prepend www to the URL, remove the setting from
# the environment entirely. Otherwise, set to 'True' (or anything tbh).
PREPEND_WWW = True

# See https://devcenter.heroku.com/articles/memcachier#django
environ['MEMCACHE_SERVERS'] = get_env_variable('MEMCACHIER_SERVERS').replace(',', ';')
environ['MEMCACHE_USERNAME'] = get_env_variable('MEMCACHIER_USERNAME')
environ['MEMCACHE_PASSWORD'] = get_env_variable('MEMCACHIER_PASSWORD')

CACHES = {
    'default': {
        'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',

        # Use binary memcache protocol (needed for authentication)
        'BINARY': True,

        # TIMEOUT is not the connection timeout! It's the default expiration
        # timeout that should be applied to keys! Setting it to `None`
        # disables expiration.
        'TIMEOUT': None,

        'OPTIONS': {
            # Enable faster IO
            'tcp_nodelay': True,

            # Keep connection alive
            'tcp_keepalive': True,

            # Timeout settings
            'connect_timeout': 2000, # ms
            'send_timeout': 750 * 1000, # us
            'receive_timeout': 750 * 1000, # us
            '_poll_timeout': 2000, # ms

            # Better failover
            'ketama': True,
            'remove_failed': 1,
            'retry_timeout': 2,
            'dead_timeout': 30,
        }
    }
}


# https
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# # HSTS
# SECURE_HSTS_SECONDS = 31536000 # 1 year
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True


# Sentry
# https://devcenter.heroku.com/articles/sentry#integrating-with-python-or-django
# via https://simonwillison.net/2017/Oct/17/free-continuous-deployment/# Step_4_Monitor_errors_with_Sentry_75

SENTRY_DSN = os.environ.get('SENTRY_DSN')

if SENTRY_DSN:
    INSTALLED_APPS += (
        'raven.contrib.django.raven_compat',
    )
    RAVEN_CONFIG = {
        'dsn': SENTRY_DSN,
        'release': os.environ.get('HEROKU_SLUG_COMMIT', ''),
    }

    
#############################################################################
# HINES-SPECIFIC SETTINGS.
