from django.conf import settings
from django.db import connection
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from redis import Redis

if (
    hasattr(settings, "REDIS_URL")
    and settings.REDIS_URL
    and hasattr(settings, "HINES_CACHE_TYPE")
    and settings.HINES_CACHE_TYPE == "redis"
):
    redis = Redis.from_url(settings.REDIS_URL)
else:
    redis = None


@never_cache
def index(request):
    """
    Check that Redis (for caching), and Postgres are up and running.
    Returns an empty page and 200 status code if all is well.
    Returns a different status code if something went wrong.
    """
    if redis:
        redis.ping()
    connection.ensure_connection()
    return HttpResponse("")
