from django.db import models
from django.core.exceptions import ObjectDoesNotExist

# We'll cache aggregator results, keyed by Aggregator ID.
AGGREGATOR_CACHE = {}

class AggregatorManager(models.Manager):

    def get_current(self):
        """
        Returns the current Aggregator based on AGGREGATOR_ID setting in the project's settings.
        This is pretty much a copy of the SiteManager from django.core.
        """
        from django.conf import settings
        try:
            aid = settings.AGGREGATOR_ID
        except AttributeError:
            from django.core.exceptions import ImproperlyConfigured
            raise ImproperlyConfigured("You haven't set the Aggregator ID setting. Create an Aggregator in your database and set the AGGREGATOR_ID setting to fix this error.")
        try:
            current_aggregator = AGGREGATOR_CACHE[aid]
        except KeyError:
            try:
                current_aggregator = self.get(pk=aid)
                AGGREGATOR_CACHE[aid] = current_aggregator
            except ObjectDoesNotExist:
                """
                TODO: This is real nasty - if there's no matching Aggregator in the DB, we return an empty string.
                But if we don't do this, then we can't even load the admin, in order to add the Aggregator.
                I think it's because the Admin screens also load the context_processors used on
                the rest of the site, which need to get the current Aggregator...
                """
                current_aggregator = ''
        return current_aggregator