from .defaults import *

DEBUG = True

ALLOWED_HOSTS = ["*",]


MEDIA_ROOT = os.path.join(APPS_DIR, 'media')
MEDIA_URL = '/media/'


# Debug Toolbar settings.
if DEBUG:
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware', ]
    INSTALLED_APPS += [ 'debug_toolbar', ]
    INTERNAL_IPS = ['127.0.0.1',]

    # Stop Django handling static files in favour of Whitenoise.
    # (When DEBUG = False)
    # Need to add the app just before staticfiles, so:
    new_apps = []
    for app in INSTALLED_APPS:
        if app == 'django.contrib.staticfiles':
            new_apps.append('whitenoise.runserver_nostatic')
        new_apps.append(app)
    INSTALLED_APPS[:] = new_apps

