from django.conf import settings
from django.db import models
from django.template.defaultfilters import linebreaks
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils import timezone

from markdown import markdown

from hines.core.models import TimeStampedModelMixin
from hines.core.utils import truncate_string


class Blog(TimeStampedModelMixin, models.Model):
    """
    """
    name = models.CharField(null=False, blank=False, max_length=255,
            help_text="Full version of the name for headings, titles, etc.")

    short_name = models.CharField(null=False, blank=False, max_length=30,
            help_text="Short version of the name for navigation etc.")

    slug = models.SlugField(max_length=255)

    sort_order = models.SmallIntegerField(default=1, blank=False,
            help_text="Blogs will be sorted with lowest sort order first, then alphabetically by Name.")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['sort_order', 'name']


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

    def htmlize_text(self, text):
        """
        Given a piece of text (the intro or body), return an HTML version,
        based on the object's html_format.
        """
        if (self.html_format == self.MARKDOWN_FORMAT):
            html = markdown(text)
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

