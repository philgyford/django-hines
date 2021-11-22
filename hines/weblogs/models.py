from datetime import timedelta
import html.parser
import re

from django.conf import settings
from django.contrib import messages
from django.db import models
from django.db.models import Count
from django.template.defaultfilters import linebreaks
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags

from bs4 import BeautifulSoup
from django_comments.moderation import CommentModerator, moderator
import smartypants
from taggit.managers import TaggableManager
from taggit.models import Tag, TaggedItemBase

from hines.core import app_settings
from hines.core.models import TimeStampedModelMixin
from hines.core.utils import (
    get_site_url,
    expire_view_cache,
    markdownify,
    truncate_string,
)
from hines.custom_comments.utils import add_comment_message
from . import managers


class Blog(TimeStampedModelMixin, models.Model):
    """
    A Blog that has Posts.
    """

    name = models.CharField(
        null=False,
        blank=False,
        max_length=255,
        help_text="Full version of the name for headings, titles, etc.",
    )

    short_name = models.CharField(
        null=False,
        blank=False,
        max_length=30,
        help_text="Short version of the name for navigation etc.",
    )

    slug = models.SlugField(max_length=255)

    feed_title = models.CharField(
        null=False,
        blank=True,
        max_length=255,
        help_text="For the Blog's RSS feed of recent Posts.",
    )

    feed_description = models.CharField(
        null=False,
        blank=True,
        max_length=255,
        help_text="For the Blog's RSS feed of recent Posts.",
    )

    show_author_email_in_feed = models.BooleanField(
        default=True,
        help_text="If checked, a Post's author's email will be "
        "included in the RSS feed.",
    )

    sort_order = models.SmallIntegerField(
        default=1,
        blank=False,
        help_text="Blogs will be sorted with lowest sort order first, "
        "then alphabetically by Name.",
    )

    allow_comments = models.BooleanField(
        default=True, help_text="If true, can still be overridden in Django SETTINGS."
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["sort_order", "name"]

    @property
    def public_posts(self):
        "Returns a QuerySet of publicly-visible Posts for this Blog."
        return Post.public_objects.filter(blog=self)

    def get_absolute_url(self):
        return reverse("weblogs:blog_detail", kwargs={"blog_slug": self.slug})

    def get_absolute_url_with_domain(self):
        """
        Returns the Blog's URL but starting with "http..."
        """
        return get_site_url() + self.get_absolute_url()

    def get_rss_feed_url(self):
        return reverse("weblogs:blog_feed_posts_rss", kwargs={"blog_slug": self.slug})

    def get_feed_title(self):
        if self.feed_title:
            return self.feed_title
        else:
            return "Latest posts from {}".format(self.name)

    def popular_tags(self, num=10):
        return (
            Tag.objects.filter(
                weblogs_taggedpost_items__content_object__blog=self,
                weblogs_taggedpost_items__content_object__status=Post.Status.LIVE,
            )
            .annotate(post_count=Count("weblogs_taggedpost_items"))
            .order_by("-post_count", "slug")[:num]
        )


class TaggedPost(TaggedItemBase):
    """
    A custom through model thing for django-taggit so we can do custom things
    with tagged Posts, like get the most popular tags filtered by Blog, Status,
    etc.
    """

    content_object = models.ForeignKey("Post", on_delete=models.CASCADE)


class Post(TimeStampedModelMixin, models.Model):
    """
    TimeStampedModelMixin gives us:

    time_created
    time_modified
    """

    class Status(models.IntegerChoices):
        DRAFT = 1, "Draft"
        LIVE = 2, "Published"
        SCHEDULED = 4, "Scheduled"

    class Formats(models.IntegerChoices):
        NONE = 0, "No formatting"
        CONVERT_LINE_BREAKS = 1, "Convert line breaks"
        # Markdown, XHTML:
        MARKDOWN = 2, "Markdown"
        # Markdown, HTML5, and with extra custom processing:
        HINES_MARKDOWN = 3, "Hines Markdown"

    class FeaturedChoices(models.IntegerChoices):
        NOT_FEATURED = 0, "Not featued"
        IS_FEATURED = 1, "Featured"

    # Basic fields.
    title = models.CharField(blank=False, max_length=255, help_text="Can use HTML tags")

    excerpt = models.TextField(
        blank=True,
        help_text="Brief summary, HTML allowed. If not set, it will "
        "be a truncated version of the Intro.",
    )

    intro = models.TextField(
        blank=False, help_text="First paragraph or so of the post."
    )
    intro_html = models.TextField(
        blank=True,
        editable=False,
        help_text="Fully HTML version of the Intro, created on save",
        verbose_name="Intro HTML",
    )

    body = models.TextField(blank=True, help_text="The rest of the post text.")
    body_html = models.TextField(
        blank=True,
        editable=False,
        help_text="Fully HTML version of Body, created on save",
        verbose_name="Body HTML",
    )

    remote_url = models.URLField(
        blank=True,
        help_text="If this post is reposted from elsewhere, add the "
        "URL for the original and it will be used for the post's permalink",
    )

    time_published = models.DateTimeField(null=True, blank=False, default=timezone.now)

    slug = models.SlugField(
        max_length=255,
        unique_for_date="time_published",
        help_text="Must be unique within its date of publication",
    )

    html_format = models.PositiveSmallIntegerField(
        blank=False,
        choices=Formats.choices,
        default=Formats.HINES_MARKDOWN,
        verbose_name="HTML format",
    )

    status = models.PositiveSmallIntegerField(
        blank=False, choices=Status.choices, default=Status.DRAFT
    )

    featured = models.PositiveSmallIntegerField(
        blank=False,
        choices=FeaturedChoices.choices,
        default=FeaturedChoices.NOT_FEATURED,
    )

    blog = models.ForeignKey(
        "Blog",
        null=True,
        blank=False,
        default=1,
        related_name="posts",
        on_delete=models.CASCADE,
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        default=1,
        on_delete=models.CASCADE,
        null=True,
        blank=False,
        related_name="posts",
    )

    allow_comments = models.BooleanField(
        default=True,
        help_text="If true, can still be overridden by the Blog's "
        "equivalent setting, or in Django SETTINGS.",
    )

    comment_count = models.IntegerField(default=0, blank=False, null=False)

    last_comment_time = models.DateTimeField(blank=True, null=True)

    trackback_count = models.IntegerField(default=0, blank=False, null=False)

    # But you might want to use self.get_tags() instead, so they're in order.
    tags = TaggableManager(through=TaggedPost, blank=True)

    # All posts, no matter what their status.
    objects = models.Manager()

    # Posts that have been published.
    public_objects = managers.PublicPostsManager()

    class Meta:
        ordering = ["-time_published", "-time_created"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Format the HTML versions of the body.
        self.intro_html = self.htmlize_text(self.intro, "intro")
        self.body_html = self.htmlize_text(self.body, "body")
        self.excerpt = self.make_excerpt()

        super().save(*args, **kwargs)

        # Expire old detail page, home page, and blog home page.
        # Assumes the things used to generate the absolute_url haven't changed.
        expire_view_cache(reverse("home"))
        expire_view_cache(
            reverse("weblogs:blog_detail", kwargs={"blog_slug": self.blog.slug})
        )
        if self.time_published is not None:
            expire_view_cache(self.get_absolute_url())

    def get_absolute_url(self):
        return reverse(
            "weblogs:post_detail",
            kwargs={
                "blog_slug": self.blog.slug,
                "year": self.time_published.strftime("%Y"),
                "month": self.time_published.strftime("%m"),
                "day": self.time_published.strftime("%d"),
                "post_slug": self.slug,
            },
        )

    def get_absolute_url_with_domain(self):
        """
        Returns the Post's URL but starting with "http..."
        """
        return get_site_url() + self.get_absolute_url()

    def get_previous_post(self):
        "Gets the previous public Post, by time_published."
        return (
            Post.public_objects.filter(
                blog=self.blog, time_published__lt=self.time_published
            )
            .order_by("-time_published")
            .first()
        )

    def get_next_post(self):
        "Gets the next public Post, by time_published."
        return (
            Post.public_objects.filter(
                blog=self.blog, time_published__gt=self.time_published
            )
            .order_by("time_published")
            .first()
        )

    def get_tags(self):
        return self.tags.all().order_by("name")

    def get_visible_trackbacks(self):
        if self.trackback_count == 0:
            return None
        else:
            return self.trackbacks.filter(is_visible=True)

    @property
    def status_str(self):
        """
        Returns the text version of the Post's status. e.g. "Draft".
        """
        choices = {a: b for a, b in self.Status.choices}
        if self.status in choices:
            return choices[self.status]
        else:
            return None

    @property
    def title_text(self):
        """A Post title containing no HTML.
        Suitable for RSS feeds, <meta> tags, etc.
        Replaces <cite> tags with curly single quotes.
        Strips any other HTML tags.
        """
        title = self.title.replace("<cite>", "‘").replace("</cite>", "’")
        title = strip_tags(title).strip()
        return title

    @property
    def excerpt_text(self):
        """A Post excerpt containing no HTML.
        Suitable for RSS feeds, <meta> tags, etc.
        Replaces <cite> tags with curly single quotes.
        Strips any other HTML tags.
        """
        excerpt = self.excerpt.replace("<cite>", "‘").replace("</cite>", "’")
        excerpt = strip_tags(excerpt).strip()
        return excerpt

    def htmlize_text(self, text, field):
        """
        Given a piece of text (the intro or body), return an HTML version,
        based on the object's html_format.

        text - The text/html to htmlize
        field - Either "intro" or "body".
        """
        if self.html_format == self.Formats.HINES_MARKDOWN:
            html = markdownify(text, output_format="html5")
            html = self.add_section_markers_to_html(html, field)
        elif self.html_format == self.Formats.MARKDOWN:
            html = markdownify(text)
        elif self.html_format == self.Formats.CONVERT_LINE_BREAKS:
            html = linebreaks(text)
        else:
            # No formatting; it's already HTML.
            html = text

        html = smartypants.smartypants(html)
        return html

    def add_section_markers_to_html(self, html, field):
        """Adds secton links and ids to elements after <hr>s in body.

        For the element immeditaely after an <hr>, it (a) gives it an
        id attribute and (b) inserts an anchor linking to that id:

            <p id="s2"><a href="#s2" ...>§</a> ...</p>

        Keyword arguments:
        html - String, the HTML to modify and return
        field -- String, either "intro" or "body". If "intro", the
            html isn't modified.
        """
        if field == "body":
            # We use html.parser as that doesn't add <html> amd <body> tags.
            soup = BeautifulSoup(html, "html.parser")
            hrs = soup.find_all("hr")
            for n, hr in enumerate(hrs):
                id = "s{}".format(n + 2)
                # Create the <a> tag:
                anchor = soup.new_tag(
                    "a",
                    href="#{}".format(id),
                    title="Link to this section",
                    # Inline style on the off-chance it's used by RSS readers:
                    style="text-decoration:none;",
                )
                anchor["class"] = "section-anchor"
                anchor.string = "§"
                # All the elements into which we'll insert an anchor
                # (assuming it directly follows an <hr>):
                el = hr.find_next(["p", "h2", "h3", "h4" "h5", "h6"])
                if el is not None:
                    # Set the ID of the <p> etc...
                    el.attrs["id"] = id
                    # ...prepend a space, then prepemd the <a>...
                    el.insert(0, " ")
                    el.insert(0, anchor)
            html = soup.encode(formatter="html5").decode()
        return html

    def make_excerpt(self):
        """
        For generating the excerpt on a Post.

        We allow HTML if self.excerpt is set, assuming it uses sensible tags.

        If the excerpt is not set, we use a truncated version of intro + body,
        with no HTML tags.

        Note: This should be done AFTER making the intro_html and body_html
        elements, as we need to strip the HTML (which we can't do by
        using intro and body if they're in, say, Markdown).
        """
        if self.excerpt:
            text = self.excerpt
        else:
            text = "{} {}".format(self.intro_html, self.body_html)
            # The HTML texts will contain entities like '&#8217;' which we
            # don't want in an excerpt, so:
            text = html.unescape(text)
            text = truncate_string(
                text, strip_html=True, chars=100, at_word_boundary=True
            )
            # Remove any section anchors put in by add_section_markers_to_html()
            text = text.replace("§ ", "")
        return text

    @property
    def main_image_url(self):
        """The URL of the image to use for meta tags, if any.
        It's the first image from the intro or, if there isn't one, the
        first image from the body.

        Returns the URL of that image, or an empty string if there isn't one.
        """
        pattern = r'<img[^>]*?src="([^"]*?)"'
        url = ""

        intro_match = re.search(pattern, self.intro_html)

        if intro_match:
            url = intro_match.group(1)
        else:
            body_match = re.search(pattern, self.body_html)

            if body_match:
                url = body_match.group(1)

        return url

    @property
    def comments_are_open(self):
        """
        Ignoring the various on/off switches for allowing comments,
        focusing only on the COMMENTS_CLOSE_AFTER_DAYS setting, are
        comments possible based on that?

        If the setting is None, this returns True
        If the setting is set then:
            If the Post is within the time limit, this returns True
            If the Post is too old, this returns False
        """
        cutoff_days = app_settings.COMMENTS_CLOSE_AFTER_DAYS
        if cutoff_days is None:
            # Means ignore this setting
            return True

        cutoff_time = timezone.now() - timedelta(days=cutoff_days)
        if self.time_published >= cutoff_time:
            # The post is within the cutoff, so comments allowed
            return True
        else:
            # The post is too old, so comments no longer allowed
            return False

    @property
    def comments_allowed(self):
        """
        Returns a boolean indicating whether new comments are allowed on this.
        """
        if app_settings.COMMENTS_ALLOWED is not True:
            return False

        elif self.blog.allow_comments is False:
            return False

        elif self.allow_comments is False:
            return False

        else:
            return self.comments_are_open


class PostCommentModerator(CommentModerator):
    """
    In addition to what we do in Post.comments_allowed, this should also
    ensure that:

    * We could enable email_notifications
    * If something automatedly submits a Comment on a Post that's older
      than COMMENTS_CLOSE_AFTER_DAYS, it will just be discarded.

    https://django-contrib-comments.readthedocs.io/en/latest/moderation.html
    """

    # Should comments require moderation before publishing?
    auto_moderate_field = "time_published"
    # Set this to:
    #   None - No moderation, publish immediately
    #   0 - Always moderate, never publish immediately
    #   n - Any other integer, only moderate when the post is this
    #       many days old.
    moderate_after = None

    # No more comments are allowed at all after this many days:
    auto_close_field = "time_published"
    close_after = app_settings.COMMENTS_CLOSE_AFTER_DAYS

    # This field on a Post is what we look at to see if comments are allowed on it:
    enable_field = "allow_comments"

    # Whether to send an email to site staff when there's a new comment:
    email_notification = False

    def allow(self, comment, content_object, request):
        """
        While this slightly duplicates Post.comments_allowed() it
        ensures that our custom things (settings.HINES_COMMENTS_ALLOWED
        and Blog.allow_comments) are taken into account in this
        moderator.

        If this returns False, then a submitted comment is just
        disappeared.
        """
        result = super().allow(comment, content_object, request)

        if not result:
            # Default method already soys NO, so:
            return False
        elif content_object.comments_allowed:
            return True
        else:
            return False

    def moderate(self, comment, content_object, request):
        """
        All we do here is:

        * Get the result from the parent moderate() method.
        * If the message is to be moderated, add a flash message
          explaining this.
        * Return the result.
        """
        result = super().moderate(comment, content_object, request)

        if result is True:
            message_content = (
                "Thanks for your comment. "
                "All comments must be checked before publishing, "
                "so it should appear soon."
            )
            add_comment_message(request, messages.SUCCESS, message_content)

        return result


moderator.register(Post, PostCommentModerator)


class Trackback(TimeStampedModelMixin, models.Model):
    """
    Used to store info about trackbacks that arrived in the old Movable Type
    version of this site.

    TimeStampedModelMixin gives us:

    time_created
    time_modified
    """

    post = models.ForeignKey(
        "Post",
        null=False,
        blank=False,
        related_name="trackbacks",
        on_delete=models.CASCADE,
    )
    title = models.CharField(blank=False, max_length=255)
    excerpt = models.TextField(blank=True, default="")
    url = models.URLField(blank=True, default="", verbose_name="URL")
    ip_address = models.GenericIPAddressField(
        blank=True, null=True, verbose_name="IP Address", default=None
    )
    blog_name = models.CharField(blank=False, max_length=255)
    is_visible = models.BooleanField(
        default=True, help_text="Should this be displayed on the site?"
    )

    class Meta:
        ordering = ["-time_created"]
        unique_together = (("post", "url"),)

    def __str__(self):
        return self.title

    def set_parent_trackback_data(self):
        """
        After saving or deleting a Trackback we have to set the trackback_count
        on the Post it's attached to.

        Called from post_delete and post_save signals.
        """
        post = self.post

        qs = Trackback.objects.filter(post=post, is_visible=True).order_by()

        post.trackback_count = qs.count()

        post.save()
