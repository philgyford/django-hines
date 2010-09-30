from django.db import models
from django.core.urlresolvers import reverse
from managers import AggregatorManager
from django.contrib.sites.models import Site


class Aggregator(models.Model):
    """
    Adding some fields that apply to the entire site.
    We should use Aggregator rather than Site where possible elsewhere I think.
    eg, Aggregator.objects.get_current() instead of Site.objects.get_current()
    """
    site = models.OneToOneField(Site, primary_key=True)
    remote_entries_feed_url = models.URLField(blank=True, help_text="If you use a service like Feedburner to host your feeds, add the URL of the feed that aggregates all the Blogs' entry feeds here. Then the URL for the local feed will be hidden.")
    remote_comments_feed_url = models.URLField(blank=True, help_text="If you use a service like Feedburner to host your feeds, add the URL of the feed of Comments on All Entries. Then the URL for the local feed will be hidden.")
    enable_comments = models.BooleanField(default=True, 
                            help_text='Uncheck to disallow commenting everywhere across the site. Overrides Blog- and Entry-level permissions.')
    
    objects = AggregatorManager()
    
    def get_entries_feed_url(self):
        if (self.remote_entries_feed_url):
            return self.remote_entries_feed_url
        else:
            return reverse('aggregator_entries_feed')
    
    def get_comments_feed_url(self):
        if (self.remote_comments_feed_url):
            return self.remote_comments_feed_url
        else:
            return reverse('aggregator_comments_feed')

    