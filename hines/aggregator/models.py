from django.db import models
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from managers import AggregatorManager


class Aggregator(models.Model):
    """
    There should be one aggregator defined for each Site.
    It's just used to hold a few site-wide things, like overall RSS feeds etc.
    Part of me thinks this really should just be a child of Site, rather than a thing side-by-side...
    """
    site = models.ForeignKey(Site)
    remote_entries_feed_url = models.URLField(blank=True, help_text="If you use a service like Feedburner to host your feeds, add the URL of the feed that aggregates all the Blogs' entry feeds here. Then the URL for the local feed will be hidden.")
    enable_comments = models.BooleanField(default=True, 
                            help_text='Uncheck to disallow commenting everywhere across the site. Overrides Blog- and Entry-level permissions.')
    
    objects = AggregatorManager()
    
    class Meta:
        ordering = ['site']
        
    def __unicode__(self):
        return self.site.name
    
    def get_entries_feed_url(self):
        if (self.remote_entries_feed_url):
            return self.remote_entries_feed_url
        else:
            return reverse('aggregator_entries_feed')

    