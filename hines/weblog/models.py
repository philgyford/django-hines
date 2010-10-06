import datetime

from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import linebreaks
from django.utils.html import strip_tags
from django.db.models.signals import post_save
from django.contrib.comments import Comment
from customcomments.models import CommentOnEntry
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.core.urlresolvers import reverse
from aggregator.models import Aggregator
from shortcuts import smart_truncate

from markdown import markdown

from managers import BlogManager, FeaturedEntryManager, LiveEntryManager
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase


class Blog(models.Model):
    '''
    A single blog on the site. Each blog has its own URL structure and its own Entries.
    '''
    name = models.CharField(max_length=255, help_text="Full version of the name, used for titles etc.")
    short_name = models.CharField(max_length=30, help_text="Short version of the name used for things like navigation links")
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=255)
    enable_comments = models.BooleanField(default=True, help_text="Uncheck to disallow commenting on this Blog. Can be overridden by 'Enable comments' on the Aggregator, but overrides Entry-level permissions.")
    remote_entries_feed_url = models.URLField(blank=True, help_text="If you use a service like Feedburner to host your feeds, add the URL for this Blog's feed here. Then the URL for the local feed will be hidden.")
    site = models.ForeignKey(Site, blank=False)
    sort_order = models.SmallIntegerField(default=1, blank=False, help_text="Blogs will be sorted on the site with lowest Sort Order first, then alphabetically by Name.")
    
    # This may be set by calling BlogManager.with_entries()
    entries = []
    
    objects = BlogManager()
    on_site = CurrentSiteManager()
    
    class Meta:
        ordering = ['sort_order', 'name']
        
    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('weblog_blog_index', (), { 'blog_slug': self.slug })
    
    def get_entries_feed_url(self):
        if (self.remote_entries_feed_url):
            return self.remote_entries_feed_url
        else:
            return reverse('weblog_entries_feed', kwargs={ 'blog_slug': self.slug })


class TaggedEntry(TaggedItemBase):
    '''
    A custom through model thing for django-taggit so we can do custom things with tagged Entries.
    '''
    content_object = models.ForeignKey('Entry')


class Entry(models.Model):
    '''
    A single Entry. An Entry belongs to a single Blog.
    '''
    # The same as Movable Type.
    DRAFT_STATUS = 1
    LIVE_STATUS = 2
    SCHEDULED_STATUS = 4
    STATUS_CHOICES = (
        (DRAFT_STATUS, 'Draft'),
        (LIVE_STATUS, 'Published'),
        # (SCHEDULED_STATUS, 'Scheduled'),
    )
    
    NO_FORMAT = 0
    CONVERT_LINE_BREAKS_FORMAT = 1
    MARKDOWN_FORMAT = 2
    FORMAT_CHOICES = (
        (NO_FORMAT, 'No formatting'),
        (CONVERT_LINE_BREAKS_FORMAT, 'Convert line breaks'),
        (MARKDOWN_FORMAT, 'Markdown'),
    )
    
    # Basic fields.
    title = models.CharField(blank=False, max_length=255)
    excerpt = models.TextField(blank=True, help_text="Brief summary, no HTML. If not set, it will be a truncated version of the Body.")
    body = models.TextField(blank=False, help_text="First paragraph or so of the entry.")
    body_html = models.TextField(blank=True, editable=False)
    body_more = models.TextField(blank=True, help_text="The rest of the entry text.")
    body_more_html = models.TextField(blank=True, editable=False)
    remote_url = models.URLField(blank=True, help_text="If this entry is reposted from elsewhere, add the URL for that location here and it will be used for the entry's permalink")
    
    # Metadata
    created_date = models.DateTimeField(auto_now_add=True)
    last_edited_date = models.DateTimeField(auto_now=True)
    published_date = models.DateTimeField(default=datetime.datetime.now)
    slug = models.SlugField(max_length=255, unique_for_date='published_date', 
                            help_text='Must be unique within its date of publication')
    author = models.ForeignKey(User)
    enable_comments = models.BooleanField(default=True, 
                            help_text='Can be overridden at the Blog and Aggregator level')
    num_comments = models.IntegerField(editable=False, default=0)
    featured = models.BooleanField(default=False)
    format = models.IntegerField(choices=FORMAT_CHOICES, default=MARKDOWN_FORMAT)
    status = models.IntegerField(choices=STATUS_CHOICES, default=LIVE_STATUS)
    blog = models.ForeignKey(Blog, default=1)
    site = models.ForeignKey(Site, blank=False, editable=False)

    # Managers
    # Need to be this way around so that non-live entries will show up in Admin, which uses the default (first) manager.
    objects = models.Manager()
    live = LiveEntryManager()
    featured_set = FeaturedEntryManager()
    on_site = CurrentSiteManager()
    
    tags = TaggableManager(through=TaggedEntry)
    
    @property
    def comments(self):
        """Return published comments"""
        from django.contrib.comments.models import Comment
        return Comment.objects.for_model(self).filter(is_public=True)
        
    class Meta:
        ordering = ['-published_date']
        verbose_name_plural = 'entries'
        
    def __unicode__(self):
        return self.title
    
    def save(self, force_insert=False, force_update=False):
        # Format the HTML versions of the body.
        self.body_html = self.htmlize_text(self.body)
        self.body_more_html = self.htmlize_text(self.body_more)
        self.excerpt = self.make_excerpt()
        self.site = self.blog.site
        super(Entry, self).save(force_insert, force_update)
    
    def get_absolute_url(self):
        if (self.remote_url):
            return self.remote_url
        else:
            return self.get_absolute_local_url()

    def htmlize_text(self, text):
        if (self.format == self.MARKDOWN_FORMAT):
            html = markdown(text)
        elif (self.format == self.CONVERT_LINE_BREAKS_FORMAT):
            html = linebreaks(text)
        else:
            # No formatting.
            html = text
        return html
        
    @models.permalink
    def get_absolute_local_url(self):
        return ('weblog_entry_detail', (), {  'blog_slug': self.blog.slug,
                                            'year': self.published_date.strftime("%Y"),
                                            'month': self.published_date.strftime("%m"),
                                            'day': self.published_date.strftime("%d"),
                                            'slug': self.slug })

    def get_next_published(self):
        return self.get_next_by_published_date(
                                blog__exact = self.blog,
                                status__exact = self.LIVE_STATUS,
                            )

    def get_previous_published(self):
        return self.get_previous_by_published_date(
                                blog__exact = self.blog,
                                status__exact = self.LIVE_STATUS,
                            )

    def comments_enabled(self):
        current_aggregator = Aggregator.objects.get_current()

        if not current_aggregator.enable_comments:
            return False
        elif not self.blog.enable_comments:
            return False
        elif not self.enable_comments:
            return False
        else:
            return True
        
    def make_excerpt(self):
        """
        For generating the excerpt on an Entry.
        If the excerpt is not set, we use a truncated version of body + body_more, with no HTML tags.
        """
        if self.excerpt:
            return strip_tags(self.excerpt)
        else:
            excerpt = strip_tags(self.body)
            return smart_truncate(excerpt, 100)


from django.contrib.comments.moderation import moderator, CommentModerator, AlreadyModerated

class EntryModerator(CommentModerator):
    """
    Custom moderator that lets us enable comments at Entry, Blog or Aggregator level.
    We could maybe move this to customcomments/moderation.py but it works here, so it's staying for a bit.
    """
    email_notification = False
    enable_field = 'enable_comments'

    def allow(self, comment, content_object, request):
        """
        Turning comments off at the Blog and Aggregator level override the Entry-level permissions.
        """
        current_aggregator = Aggregator.objects.get_current()
        if not current_aggregator.enable_comments:
            return False
        elif not content_object.blog.enable_comments:
            return False
        else:
            return super(EntryModerator, self).allow(comment, content_object, request)

try:
    moderator.register(Entry, EntryModerator)
except AlreadyModerated:
    # Safeguard against the models module being imported multiple
    # times (thus registering multiple times and throwing this error)
    pass


def comment_post_save_handler(sender, **kwargs):
    """
    When we save a comment then we update the num_comments field on the associated Entry.
    NOTE: If we use comments on anything other than Entries then we'll either have to
    customise this, or give those new objects num_comments fields too, and then this should 
    also work for them.
    """
    comment = kwargs['instance']
    entry = comment.content_object
    if type(entry) is Entry:
        num_comments_on_entry = CommentOnEntry.objects.filter(
            content_type = comment.content_type,
            object_pk = comment.object_pk,
            is_public = 1,
            is_removed = 0
        ).count()
        entry.num_comments = num_comments_on_entry
        entry.save()
post_save.connect(comment_post_save_handler, sender=CommentOnEntry)

