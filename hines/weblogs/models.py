from django.conf import settings
from django.db import models
from django.db.models import Count
from django.template.defaultfilters import linebreaks
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils import timezone

from markdownx.utils import markdownify
from taggit.managers import TaggableManager
from taggit.models import Tag, TaggedItemBase

from hines.core.models import TimeStampedModelMixin
from hines.core.utils import truncate_string
from . import managers


class Blog(TimeStampedModelMixin, models.Model):
    """
    A Blog that has Posts.
    """
    name = models.CharField(null=False, blank=False, max_length=255,
            help_text="Full version of the name for headings, titles, etc.")

    short_name = models.CharField(null=False, blank=False, max_length=30,
            help_text="Short version of the name for navigation etc.")

    slug = models.SlugField(max_length=255)

    feed_title = models.CharField(null=False, blank=True, max_length=255,
            help_text="For the Blog's RSS feed of recent Posts.")

    feed_description = models.CharField(null=False, blank=True, max_length=255,
            help_text="For the Blog's RSS feed of recent Posts.")

    show_author_email_in_feed = models.BooleanField(default=True,
            help_text="If checked, a Post's author's email will be included in the RSS feed.")

    sort_order = models.SmallIntegerField(default=1, blank=False,
            help_text="Blogs will be sorted with lowest sort order first, then alphabetically by Name.")

    allow_comments = models.BooleanField(default=True,
            help_text="If true, can still be overridden in Django SETTINGS.")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['sort_order', 'name']

    @property
    def public_posts(self):
        "Returns a QuerySet of publicly-visible Posts for this Blog."
        return Post.public_objects.filter(blog=self)

    def get_absolute_url(self):
        return reverse('hines:blog_detail',
                            kwargs={
                                'blog_slug': self.slug,
                            })

    def popular_tags(self, num=10):
        return Tag.objects.filter(
            weblogs_taggedpost_items__content_object__blog=self,
            weblogs_taggedpost_items__content_object__status=Post.LIVE_STATUS,
        )\
        .annotate(post_count=Count('weblogs_taggedpost_items'))\
        .order_by('-post_count', 'slug')[:num]


class TaggedPost(TaggedItemBase):
    """
    A custom through model thing for django-taggit so we can do custom things
    with tagged Posts, like get the most popular tags filtered by Blog, Status,
    etc.
    """
    content_object = models.ForeignKey('Post')


class Post(TimeStampedModelMixin, models.Model):

    DRAFT_STATUS = 1
    LIVE_STATUS = 2
    # SCHEDULED_STATUS = 4
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

    NOT_FEATURED = 0
    IS_FEATURED = 1
    FEATURED_CHOICES = (
        (NOT_FEATURED, 'Not featured'),
        (IS_FEATURED, 'Featured'),
    )

    # Basic fields.
    title = models.CharField(blank=False, max_length=255)

    excerpt = models.TextField(blank=True,
            help_text="Brief summary, no HTML. If not set, it will be a truncated version of the Intro.")

    intro = models.TextField(blank=False,
            help_text="First paragraph or so of the post.")
    intro_html = models.TextField(blank=True, editable=False,
            help_text="Fully HTML version of the Intro, created on save",
            verbose_name='Intro HTML')

    body = models.TextField(blank=True,
            help_text="The rest of the post text.")
    body_html = models.TextField(blank=True, editable=False,
            help_text="Fully HTML version of Body, created on save",
            verbose_name='Body HTML')

    remote_url = models.URLField(blank=True,
            help_text="If this post is reposted from elsewhere, add the URL for the original and it will be used for the post's permalink")

    time_published = models.DateTimeField(null=True, blank=True)

    slug = models.SlugField(max_length=255, unique_for_date='time_published',
            help_text='Must be unique within its date of publication')

    html_format = models.PositiveSmallIntegerField(blank=False,
                choices=FORMAT_CHOICES, default=MARKDOWN_FORMAT,
                verbose_name='HTML format')

    status = models.PositiveSmallIntegerField(blank=False,
                choices=STATUS_CHOICES, default=DRAFT_STATUS)

    featured = models.PositiveSmallIntegerField(blank=False,
                choices=FEATURED_CHOICES, default=NOT_FEATURED)

    blog = models.ForeignKey('Blog', null=True, blank=False, default=1,
                related_name='posts')

    author = models.ForeignKey(settings.AUTH_USER_MODEL, default=1,
                on_delete=models.CASCADE, null=True, blank=False,
                related_name='posts')

    allow_comments = models.BooleanField(default=True,
            help_text="If true, can still be overridden by the Blog's equivalent setting, or in Django SETTINGS.")

    # But you might want to use self.get_tags() instead, so they're in order.
    tags = TaggableManager(through=TaggedPost)

    objects = models.Manager()

    public_objects = managers.PublicPostsManager()

    class Meta:
        ordering = ['-time_published', '-time_created']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Format the HTML versions of the body.
        self.intro_html = self.htmlize_text(self.intro)
        self.body_html = self.htmlize_text(self.body)
        self.excerpt = self.make_excerpt()

        if self.time_published is None and self.status == self.LIVE_STATUS:
            # Published for the first time!
            self.time_published = timezone.now()

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('hines:post_detail',
                            kwargs={
                                'blog_slug': self.blog.slug,
                                'year': self.time_published.strftime("%Y"),
                                'month': self.time_published.strftime("%m"),
                                'day': self.time_published.strftime("%d"),
                                'post_slug': self.slug,
                            })

    def get_previous_post(self):
        "Gets the previous public Post, by time_published."
        return Post.public_objects.filter(
                                        blog=self.blog,
                                        time_published__lt=self.time_published
                                    )\
                                   .order_by('-time_published')\
                                   .first()

    def get_next_post(self):
        "Gets the next public Post, by time_published."
        return Post.public_objects.filter(
                                        blog=self.blog,
                                        time_published__gt=self.time_published
                                    )\
                                   .order_by('time_published')\
                                   .first()

    def get_tags(self):
        return self.tags.all().order_by('name')

    def htmlize_text(self, text):
        """
        Given a piece of text (the intro or body), return an HTML version,
        based on the object's html_format.
        """
        if (self.html_format == self.MARKDOWN_FORMAT):
            html = markdownify(text)
        elif (self.html_format == self.CONVERT_LINE_BREAKS_FORMAT):
            html = linebreaks(text)
        else:
            # No formatting; it's already HTML.
            html = text
        return html

    def make_excerpt(self):
        """
        For generating the excerpt on a Post.
        If the excerpt is not set, we use a truncated version of intro + body,
        with no HTML tags.

        Note: This should be done AFTER making the intro_html and body_html
        elements, as we need to strip the HTML (which we can't do by
        using intro and body if they're in, say, Markdown).
        """
        if self.excerpt:
            return strip_tags(self.excerpt)
        else:
            text = '{} {}'.format(self.intro_html, self.body_html)
            return truncate_string(
                    text, strip_html=True, chars=100, at_word_boundary=True)

    @property
    def comments_allowed(self):
        """
        Returns a boolean indicating whether new comments are allowed on this.
        """
        if hasattr(settings, 'HINES_ALLOW_COMMENTS') and settings.HINES_ALLOW_COMMENTS == False:
            return False

        elif self.blog.allow_comments == False:
            return False

        elif self.allow_comments == False:
            return False

        else:
            return True

