from django.conf import settings
from django.core.cache import DEFAULT_CACHE_ALIAS, caches
from django.core.cache.backends.base import InvalidCacheBackendError
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """
    A simple management command which clears the site-wide cache.
    From https://github.com/django-extensions/django-extensions/blob/master/django_extensions/management/commands/clear_cache.py
    """
    help = 'Fully clear site-wide cache.'

    def add_arguments(self, parser):
        parser.add_argument('--cache', action='append',
                            help='Name of cache to clear')
        parser.add_argument('--all', '-a', action='store_true', default=False,
                            dest='all_caches', help='Clear all configured caches')

    def handle(self, cache, all_caches, *args, **kwargs):
        if not cache and not all_caches:
            cache = [DEFAULT_CACHE_ALIAS]
        elif cache and all_caches:
            raise CommandError('Using both --all and --cache is not supported')
        elif all_caches:
            cache = getattr(settings, 'CACHES', {DEFAULT_CACHE_ALIAS: {}}).keys()

        for key in cache:
            try:
                caches[key].clear()
            except InvalidCacheBackendError:
                self.stderr.write('Cache "%s" is invalid!\n' % key)
            else:
                self.stdout.write('Cache "%s" has been cleared!\n' % key)
