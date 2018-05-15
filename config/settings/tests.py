from .base import *


HINES_ROOT_DIR = 'terry'


CACHES = {
    'default': {
        # Use dummy cache (ie, no caching):
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
