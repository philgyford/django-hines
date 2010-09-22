from django.db import models
from django.contrib.sites.models import Site
    
# We'll cache aggregator results, keyed by Site ID (same as Aggregator ID).
AGGREGATOR_CACHE = {}

class AggregatorManager(models.Manager):

    def get_current(self):
        """
        Returns the current Aggregator based on AGGREGATOR_ID setting in the project's settings.
        This is pretty much a copy of the SiteManager from django.core.
        """
        
        current_site = Site.objects.get_current()
        
        try:
            current_aggregator = AGGREGATOR_CACHE[current_site.id]
        except KeyError:
            try:
                current_aggregator = self.get(pk__exact=current_site.id)
                AGGREGATOR_CACHE[current_site.id] = current_aggregator
            except:
                """
                TODO: This is real nasty - if there's no matching Aggregator in the DB, we return an empty string.
                But if we don't do this, then we can't even load the admin, in order to add the Aggregator.
                I think it's because the Admin screens also load the context_processors used on
                the rest of the site, which need to get the current Aggregator...
                """
                current_aggregator = ''
        return current_aggregator
