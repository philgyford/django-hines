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
    remote_entries_feed_url = models.URLField(blank=True, 
        verbose_name='Remove entries feed URL',
        help_text="If you use a service like <a href=\"http://feedburner.google.com/\">Feedburner</a> to host your feeds, add the URL of the feed that aggregates all the Blogs' entry feeds here. Then the URL for the local feed will be hidden.")
    remote_comments_feed_url = models.URLField(blank=True, 
        verbose_name='Remote comments feed URL',
        help_text="If you use a service like <a href=\"http://feedburner.google.com/\">Feedburner</a> to host your feeds, add the URL of the feed of Comments on All Entries. Then the URL for the local feed will be hidden.")
    enable_comments = models.BooleanField(default=True, 
       help_text='Uncheck to disallow commenting everywhere across the site. Overrides Blog- and Entry-level permissions.')
    allowed_comment_tags = models.CharField(blank=True, max_length=255, 
        help_text="Tags and attributes that users can use in comments, if any. Of the form \"a:href:title blockquote em img:src pre ul ol li\".")
    test_comments_for_spam = models.BooleanField(default=False,
        help_text="If checked and one of the API keys is set, comments will be filtered for spam. If both API keys are set, only TypePad Antispam will be used.")
    typepad_antispam_api_key = models.CharField(blank=True, max_length=50,
        verbose_name='TypePad AntiSpam API key',
        help_text="The API key for the <a href=\"http://antispam.typepad.com/\">TypePad AntiSpam</a> service")
    akismet_api_key = models.CharField(blank=True, max_length=50,
        verbose_name='Akismet API key',
        help_text="The API key for the <a href=\"http://akismet.com/\">Akismet</a> anti comment spam service")
    
    objects = AggregatorManager()
    

    def _get_allowed_tags_list(self):
        """
        If allowed_tags is 'a:href:name b img:src' this will return ['a','b','img']
        """
        from django.conf import settings
        tags = []
        allowed_tags = self.allowed_comment_tags.split(' ')
        for allowed_tag in allowed_tags:
            tag_attrs = allowed_tag.split(':')
            tags.append(tag_attrs[0])
        return tags   
    allowed_tags_list = property(_get_allowed_tags_list)


    def _get_allowed_attrs_dict(self):
        """
        If allowed_tags is 'a:href:name b img:src' this will return 
        {'a':['href','name'], 'img':['src']}
        """
        from django.conf import settings
        attrs = {}
        allowed_tags = self.allowed_comment_tags.split(' ')
        for allowed_tag in allowed_tags:
            tag_attrs = allowed_tag.split(':')
            if len(tag_attrs) > 1:
                attrs[tag_attrs[0]] = tag_attrs[1:]
        return attrs
    allowed_attrs_dict = property(_get_allowed_attrs_dict)


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

    
