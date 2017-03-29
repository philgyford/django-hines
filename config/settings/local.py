from .defaults import *

DEBUG = True

ALLOWED_HOSTS = ["*",]


STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'


# Debug Toolbar settings.
if DEBUG:
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware', ]
    INSTALLED_APPS += ['debug_toolbar', ]
    INTERNAL_IPS = ['127.0.0.1', '192.168.33.1', '0.0.0.0', '109.246.8.73',]

