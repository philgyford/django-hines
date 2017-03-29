from .defaults import *

DEBUG = True

ALLOWED_HOSTS = ["*",]


MEDIA_ROOT = os.path.join(APPS_DIR, 'media')
MEDIA_URL = '/media/'


# Debug Toolbar settings.
if DEBUG:
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware', ]
    INSTALLED_APPS += ['debug_toolbar', ]
    INTERNAL_IPS = ['127.0.0.1',]

