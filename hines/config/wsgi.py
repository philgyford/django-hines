"""
WSGI config for hines project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""
# Fix django closing connection to MemCachier after every request (#11331)
# From https://devcenter.heroku.com/articles/memcachier#django
from django.core.cache.backends.memcached import BaseMemcachedCache
from django.core.wsgi import get_wsgi_application

BaseMemcachedCache.close = lambda self, **kwargs: None


application = get_wsgi_application()
