from collections import OrderedDict
import datetime
import re

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import InvalidPage
from django.db import connection
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseServerError,
)
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import requires_csrf_token
from django.views.generic import ListView, TemplateView
from django.views.generic.base import RedirectView
from django.views.generic.dates import DayMixin, MonthMixin, YearMixin

from ditto.flickr.models import Photo, Photoset
from ditto.pinboard.models import Bookmark
from ditto.twitter.models import Tweet
from spectator.core.models import Creator
from spectator.reading.models import Publication
from spectator.reading.views import ReadingHomeView as SpectatorReadingHomeView
from hines.core import app_settings
from hines.core.utils import make_date
from hines.weblogs.models import Blog
from .paginator import DiggPaginator


@requires_csrf_token
def bad_request(request, *args, **kwargs):
    """
    Adds ``STATIC_URL`` to the context.
    """
    context = {"STATIC_URL": settings.STATIC_URL}
    t = get_template(kwargs.get("template_name", "errors/400.html"))
    return HttpResponseBadRequest(t.render(context, request))


@requires_csrf_token
def permission_denied(request, *args, **kwargs):
    """
    Adds ``STATIC_URL`` to the context.
    """
    context = {"STATIC_URL": settings.STATIC_URL}
    t = get_template(kwargs.get("template_name", "errors/403.html"))
    return HttpResponseForbidden(t.render(context, request))


@requires_csrf_token
def page_not_found(request, *args, **kwargs):
    """
    Mimics Django's 404 handler but with a different template path.
    """
    context = {
        "STATIC_URL": settings.STATIC_URL,
        "request_path": request.path,
    }
    t = get_template(kwargs.get("template_name", "errors/404.html"))
    return HttpResponseNotFound(t.render(context, request))


@requires_csrf_token
def server_error(request, template_name="errors/500.html"):
    """
    Mimics Django's error handler but adds ``STATIC_URL`` to the
    context.
    """
    context = {"STATIC_URL": settings.STATIC_URL}
    t = get_template(template_name)
    return HttpResponseServerError(t.render(context, request))


def up(request):
    """
    Healthcheck page, for testing the site is up.

    Could also do:

        from redis import Redis

    and then:

        redis.ping()
    """
    connection.ensure_connection()
    return HttpResponse("")


class CacheMixin(object):
    """
    Add this mixin to a view to cache it.

    Disables caching for logged-in users.
    """

    cache_timeout = 60 * 5  # seconds

    def get_cache_timeout(self):
        return self.cache_timeout

    def dispatch(self, *args, **kwargs):
        if hasattr(self.request, "user") and self.request.user.is_authenticated:
            # Logged-in, return the page without caching.
            return super().dispatch(*args, **kwargs)
        else:
            # Unauthenticated user; use caching.
            return cache_page(self.get_cache_timeout())(super().dispatch)(
                *args, **kwargs
            )


class HomeView(CacheMixin, TemplateView):
    template_name = "hines_core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sections"] = self.get_recent_items()
        return context

    def get_recent_items(self):
        """
        Returns an OrderedDict like:
            {
                'flickr_photos_list': <QuerySet of Photos>,
                'weblog_posts_writing': <QuerySet of Posts>,
                'weblog_posts_comments': <QuerySet of Posts>,
                'pinboard_bookmark_list': <QuerySet of Bookmarks>,
            }

        It will be ordered base on whichever thing as the most recent item
        in its QuerySet.
        """
        items = {}

        for blog, posts in self._get_weblog_posts().items():
            items.update({blog: posts})
        items.update(self._get_flickr_photos())
        items.update(self._get_pinboard_bookmarks())

        def by_time_key(item):
            """
            For sorting the sets of item by date.
            item is like:
                ('flickr_photos_list', <QuerySet of Photos>)
            We assume the QuerySet is sorted, with most recent first.
            """
            qs = item[1]
            if len(qs) > 0:
                if hasattr(qs[0], "time_published"):
                    return qs[0].time_published
                else:
                    return qs[0].post_time
            return False

        # Sort the dict of items so that they're in reverse-chronological
        # order, based on their most recent post, photo, link etc.

        # Filter out any that have empty QueryStrings, or else we get an error
        # when comparing their by_time_key's below.
        items = {k: v for k, v in items.items() if len(v) > 0}

        sorted_items = OrderedDict(sorted(items.items(), key=by_time_key, reverse=True))

        return sorted_items

    def _get_section_quantity(self, section_name, subsection_name=None):
        """
        Get the number of things to display for a section.

        Expects a Django setting like:

        HINES_HOME_PAGE_DISPLAY = {
            'flickr_photos': 3,
            'pinboard_bookmarks': 3,
            'weblog_posts': {
                'writing': 3,
                'comments': 1,
            },
        }

        section_name is like 'flickr_photos' or 'weblog_posts'
        If it's 'weblog_posts', then subsection_name should be like 'writing'.
        """
        section_quantity = 0

        display = app_settings.HOME_PAGE_DISPLAY

        if section_name in display:
            section_quantity = display[section_name]
            if section_name == "weblog_posts":
                if subsection_name in section_quantity:
                    section_quantity = section_quantity[subsection_name]

        return section_quantity

    def _get_weblog_posts(self):
        """
        Returns a dict:
        e.g. assuming we have two Blogs with the short_names 'writing' and
        'comments':
            {
                'weblog_posts_writing': <QuerySet of Posts>,
                'weblog_posts_comments': <QuerySet of Posts>,
            }
        """
        posts = {}

        for blog in Blog.objects.all():
            quantity = self._get_section_quantity("weblog_posts", blog.slug)
            if quantity > 0:
                qs = blog.public_posts.all()[:quantity]
            key = "weblog_posts_{}".format(blog.slug)
            posts[key] = qs

        return posts

    def _get_flickr_photos(self):
        quantity = self._get_section_quantity("flickr_photos")
        if quantity > 0:
            photos = Photo.public_objects.all()[:quantity]
        else:
            photos = Photo.objects.none()
        return {"flickr_photo_list": photos}

    def _get_pinboard_bookmarks(self):
        quantity = self._get_section_quantity("pinboard_bookmarks")
        if quantity > 0:
            bookmarks = Bookmark.public_objects.all()[:quantity]
        else:
            bookmarks = Bookmark.objects.none()
        return {"pinboard_bookmark_list": bookmarks}


class ReadingHomeView(SpectatorReadingHomeView):
    """
    A wrapper around Spectator's ReadingHomeView so that we can redirect any
    legacy requests for /phil/reading/?y=2017 which we will redirect to
    /phil/reading/2017/.
    """

    def get(self, request, *args, **kwargs):
        year = request.GET.get("y", None)

        try:
            year = int(year)
        except (TypeError, ValueError):
            # It was missing or a string.
            year = None
        else:
            if year < 1000 or year > 9999:
                # Because the reading year archive URL expects a 4-digit number.
                year = None

        if year is not None:
            # We have a 4-digit number, so try redirecting.
            return redirect(
                "spectator:reading:reading_year_archive", year=int(year), permanent=True
            )

        return super().get(request, args, kwargs)


class WritingResourcesRedirectView(RedirectView):
    """
    Redirecting old /writing/resources/* URLs to new location.
    e.g.
    FROM: http://www.gyford.com/phil/writing/resources/2016/02/02/test.png
    TO: https://MY-BUCKET.s3.amazonaws.com/phil/weblogs/2016/02/02/test.png
    """

    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        year = kwargs.get("year", None)
        month = kwargs.get("month", None)
        day = kwargs.get("day", None)
        path = kwargs.get("path", None)

        if path is None:
            raise Http404("No path supplied.")
        else:
            return "{}weblogs/{}/{}/{}/{}".format(
                settings.MEDIA_URL, year, month, day, path
            )


class ArchiveRedirectView(RedirectView):
    """
    Redirecting old /archive/* URLs to archive.gyford.com.
    """

    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        path = kwargs.get("path", "")
        return "http://archive.gyford.com/{}".format(path)


class AuthorRedirectView(RedirectView):
    """
    Redirecting old /phil/reading/author/?id=123 requests
    """

    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        id = self.request.GET.get("id", None)
        try:
            author = Creator.objects.get(id=id)
        except Creator.DoesNotExist:
            return None
        else:
            return author.get_absolute_url()


class PublicationRedirectView(RedirectView):
    """
    Redirecting old /phil/reading/publication/?id=123 requests
    """

    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        id = self.request.GET.get("id", None)
        try:
            publication = Publication.objects.get(id=id)
        except Publication.DoesNotExist:
            return None
        else:
            return publication.get_absolute_url()


class MTSearchRedirectView(RedirectView):
    """
    Redirecting old MT CGI requests, which were for tags or searches.
    404 everything else.

    e.g. a tag on Mary's site (blog 14):
    FROM: www.gyford.com/cgi-bin/mt/mt-search.cgi?IncludeBlogs=14&tag=test%20this%20tag%28brackets%29&limit=1000  # noqa: E501
    TO: https://www.sparklytrainers.com/blog/tag/test-this-tag-brackets/

    e.g. a search on both Mary's blogs (blogs 14 and 18):
    FROM: http://www.gyford.com/cgi-bin/mt/mt-search.cgi?IncludeBlogs=14,18&search=Cordillera+Huayhuash+Circuit+plus+Inca+Trail+to+Machu+Picchu
    TO: https://www.sparklytrainers.com/?s=Cordillera+Huayhuash+Circuit+plus+Inca+Trail+to+Machu+Picchu

    e.g. a search on Overmorgen (blog 10):
    FROM: /cgi-bin/mt/mt-search.cgi?search=test+search&IncludeBlogs=10&limit=1000
    TO: https://www.google.com/search?as_sitesearch=www.overmorgen.com&q=test+search
    """

    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        blog_ids = self.request.GET.get("IncludeBlogs", None)
        tag_str = self.request.GET.get("tag", None)
        search_str = self.request.GET.get("search", None)

        if blog_ids is None:
            raise Http404("No Blog IDs supplied.")

        if tag_str is None and search_str is None:
            raise Http404("No tag or search string supplied.")

        blog_ids = blog_ids.split(",")

        if len(blog_ids) == 0:
            raise Http404("No Blog IDs supplied.")

        if "14" in blog_ids or "18" in blog_ids:
            # One of Mary's blogs.
            tag_str = self._get_wp_tag_str(tag_str)
            search_str = self._get_wp_search_str(search_str)

            if tag_str:
                url = "https://www.sparklytrainers.com/blog/tag/{}/".format(tag_str)
            else:
                url = "https://www.sparklytrainers.com/?s={}".format(search_str)

        elif "10" in blog_ids:
            # Overmorgen.
            search_str = self._get_google_search_str(search_str)
            url = (
                "https://www.google.com/search?" "as_sitesearch=www.overmorgen.com&q={}"
            ).format(search_str)

        else:
            raise Http404("Not the right combination of Blog ID, tag or search.")

        return url

    def _get_wp_tag_str(self, tag_str):
        """
        Turns a tag string from a Movable Type URL into a WordPress tag string.
        e.g. from "Val-Pitkethly-s-Cordillera-Blanca--Peru"
        to "val-pitkethlys-cordillera-blanca-peru"

        """
        if tag_str is None:
            return None

        # Removes things like apostrophes. Leaves spaces and brackets:
        tag_str = re.sub(r"[^a-zA-Z0-9 \(\)]+", "", tag_str)
        # Turns the spaces and brackets into hyphens:
        tag_str = "".join([c if c.isalnum() else "-" for c in tag_str])
        # Remove any duplicate hyphens:
        tag_str = re.sub("-+", "-", tag_str)
        # Remove any trailing hyphen:
        tag_str = tag_str.rstrip("-")
        # Everything to lowercase:
        tag_str = tag_str.lower()

        return tag_str

    def _get_wp_search_str(self, search_str):
        if search_str is None:
            return None
        # Removes most punctuation. Leaves spaces and brackets:
        search_str = re.sub(r"[^a-zA-Z0-9'\.,_ \(\)]+", "", search_str)
        search_str = search_str.replace(" ", "+")
        return search_str

    def _get_google_search_str(self, search_str):
        """
        Turns a search string from a Movable Type URL into a Google search string.
        """
        if search_str is None:
            return None

        search_str = "".join([c if c.isalnum() else "+" for c in search_str])
        return search_str


class DayArchiveView(YearMixin, MonthMixin, DayMixin, TemplateView):
    """
    Trying to keep things a bit consistent with BaseDateListView, except we
    don't have a single QuerySet we're fetching for this date, so we can't
    use it.
    """

    # Note: Disallowing empty pages will still show next/prev links to empty
    # pages as we don't currently check all the contents of next/prev pages:
    allow_empty = True
    allow_future = False
    day_format = "%d"
    month_format = "%m"
    year_format = "%Y"
    template_name = "hines_core/archive_day.html"

    def get_allow_empty(self):
        """
        Returns ``True`` if the view should display empty lists, and ``False``
        if a 404 should be raised instead.
        """
        return self.allow_empty

    def get_allow_future(self):
        """
        Returns `True` if the view should be allowed to display objects from
        the future.
        """
        return self.allow_future

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # date_list isn't used here:
        # And object_lists is a dict of data, rather than one QuerySet:
        date_list, object_lists, extra_context = self.get_dated_items()

        context.update(extra_context)

        context["sections"] = object_lists

        return context

    def get_dated_items(self):
        """
        Return (date_list, items, extra_context) for this request.
        (Although date_list and items will be None.)
        """
        year = self.get_year()
        month = self.get_month()
        day = self.get_day()

        date = _date_from_string(
            year,
            self.get_year_format(),
            month,
            self.get_month_format(),
            day,
            self.get_day_format(),
        )

        return self._get_dated_items(date)

    def _get_dated_items(self, date):
        """
        Mirroring the behaviour of BaseDateListView's method, just to keep
        things consistent.

        EXCEPT:
        - We return a dict of data as the second item, rather than a
            single QuerySet.
        - We don't allow viewing pages before HINES_FIRST_DATE.
        """
        allow_future = self.get_allow_future()
        allow_empty = self.get_allow_empty()
        first_date = self.get_first_date()

        if not allow_future and date > timezone_today():
            raise Http404(_("Future dates not available"))

        if first_date and date < first_date:
            raise Http404(_("Dates this old not available"))

        object_lists = {}

        # The order we add things to object_lists is the order in which
        # they'll appear in the page...

        for blog, posts in self._get_weblog_posts(date).items():
            object_lists.update({blog: posts})

        object_lists.update(self._get_flickr_photos(date))

        object_lists.update(self._get_pinboard_bookmarks(date))

        object_lists.update(self._get_twitter_tweets(date))

        object_lists.update(self._get_twitter_favorites(date))

        if not allow_empty:
            if len(object_lists) == 0:
                raise Http404(_("Nothing available"))

        # Count the total number of ALL items are in the QuerySets:
        object_count = 0
        for key, object_list in object_lists.items():
            object_count += len(object_list)

        return (
            None,
            object_lists,
            {
                "day": date,
                "previous_day": self.get_previous_day(date),
                "next_day": self.get_next_day(date),
                "object_count": object_count,
            },
        )

    def get_next_day(self, date):
        result = date + datetime.timedelta(days=1)

        if self.get_allow_future() or result <= timezone_today():
            return result
        else:
            return None

    def get_first_date(self):
        """
        Our custom method for getting the date set in HINES_FIRST_DATE, if any.
        If not set, return False.
        """
        if app_settings.FIRST_DATE:
            return datetime.datetime.strptime(
                app_settings.FIRST_DATE, "%Y-%m-%d"
            ).date()
        else:
            return False

    def get_previous_day(self, date):
        """
        Customised, so we don't return a previous day if it would be before
        HINES_FIRST_DATE.
        """
        first_date = self.get_first_date()
        previous_date = date - datetime.timedelta(days=1)
        if first_date and previous_date < first_date:
            return False
        else:
            return previous_date

    def _get_weblog_posts(self, date):
        """
        Returns a dict:
        e.g. assuming we have two Blogs with the short_names 'writing' and
        'comments':
            {
                'weblog_posts_writing': <QuerySet of Posts>,
                'weblog_posts_comments': <QuerySet of Posts>,
            }
        """
        posts = {}

        for blog in Blog.objects.all():
            qs = blog.public_posts.filter(time_published__date=date)
            key = "weblog_posts_{}".format(blog.slug)
            posts[key] = qs

        return posts

    def _get_flickr_photos(self, date):
        photos = Photo.public_objects.filter(taken_time__date=date, taken_granularity=0)
        return {"flickr_photo_list": photos}

    def _get_pinboard_bookmarks(self, date):
        bookmarks = Bookmark.public_objects.filter(post_time__date=date)
        return {"pinboard_bookmark_list": bookmarks}

    def _get_twitter_favorites(self, date):
        tweets = Tweet.public_favorite_objects.filter(
            post_time__date=date
        ).prefetch_related("user")
        return {"twitter_favorite_list": tweets}

    def _get_twitter_tweets(self, date):
        tweets = Tweet.public_tweet_objects.filter(
            post_time__date=date
        ).prefetch_related("user")
        return {"twitter_tweet_list": tweets}


class PaginatedListView(ListView):
    """Use this instead of ListView to provide standardised pagination."""

    paginator_class = DiggPaginator
    paginate_by = 30
    page_kwarg = "p"
    allow_empty = False

    # See hines.core.paginator for what these mean:
    paginator_body = 5
    paginator_margin = 2
    paginator_padding = 2
    paginator_tail = 2
    # If True, requesting a page number greater than the number of pages
    # will show the final page, instead of 404:
    softlimit = False

    def __init__(self, **kwargs):
        return super().__init__(**kwargs)

    def paginate_queryset(self, queryset, page_size):
        """
        Paginate the queryset, if needed.

        This is EXACTLY the same as the standard ListView.paginate_queryset()
        except for this line:
            page = paginator.page(page_number, softlimit=self.softlimit)
        Because we want to use the DiggPaginator's softlimit option.
        So that if you're viewing a page of, say, Flickr photos, and you switch
        from viewing by Uploaded Time to viewing by Taken Time, the new
        ordering might have fewer pages. In that case we want to see the final
        page, not a 404. The softlimit does that, but I can't see how to use
        it without copying all of this...
        """
        paginator = self.get_paginator(
            queryset,
            page_size,
            orphans=self.get_paginate_orphans(),
            allow_empty_first_page=self.get_allow_empty(),
            body=self.paginator_body,
            margin=self.paginator_margin,
            padding=self.paginator_padding,
            tail=self.paginator_tail,
        )
        page_kwarg = self.page_kwarg
        page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
        try:
            page_number = int(page)
        except ValueError:
            if page == "last":
                page_number = paginator.num_pages
            else:
                raise Http404(
                    _("Page is not 'last', nor can it be converted to an int.")
                )
        try:
            page = paginator.page(page_number, softlimit=self.softlimit)
            return (paginator, page, page.object_list, page.has_other_pages())
        except InvalidPage as e:
            raise Http404(
                _("Invalid page (%(page_number)s): %(message)s")
                % {"page_number": page_number, "message": str(e)}
            )


class PhotosHomeView(PaginatedListView):
    """
    We only have a single page showing photos, so doesn't make sense to put
    it in its own app. So here we are.
    """

    template_name = "hines_core/photos_home.html"
    queryset = Photo.public_objects.all()
    # Divisible by four columns:
    paginate_by = 48

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["photoset_list"] = Photoset.objects.all().order_by("-last_update_time")[
            :10
        ]

        return context


class TemplateSetMixin(object):
    """
    Lets us use a different template for a page depending on the date of its
    object (or something else).

    We should have a setting something like:

        HINES_TEMPLATE_SETS = (
            {'name': 'houston', 'start': '2000-03-01', 'end': '2000-12-31'},
            {'name': 'london', 'start': '2000-12-31', 'end': '2003-03-15'},
        )

    By default, and with this setting, if `self.object.date` falls between
    2000-03-01 and 2000-12-31 inclusive, it will use the template
    `sets/houston/[self.template_name]`.

    You can change which attribute on self.object is used by setting
    self.template_set_date_attr. Its value can be a date or datetime.

    If the View you're using doesn't have `self.object` you'll probably want
    to provide your own get_template_set_date() method to return the date
    object you need.

    The name of the chosen template set will also be set in the context data
    (or None, if no set was used).
    """

    template_name = None

    # Which attribute of self.object should be used to determine the date that
    # we use to find which Template Set to use?
    # It can be a date or datetime object.
    template_set_date_attr = "time_created"

    # Will be set to the name of the appropriate template set, if any.
    template_set = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Not sure this is the best place for this call...
        self.set_template_set()

        context["template_set"] = self.template_set

        return context

    def get_template_set_date(self):
        """
        Returns the date to use for determining which Template Set, if any
        to use.

        Defaults to using the self.template_set_date_attr attribute of
        self.object. Create your own get_template_set_date() method in your
        view class if that isn't appropriate.
        """
        if self.object:
            d = getattr(self.object, self.template_set_date_attr, None)
            if d is not None:
                if isinstance(d, datetime.date):
                    return d
                elif isinstance(d, datetime.datetme):
                    return d.date()
                else:
                    raise ImproperlyConfigured(
                        "TemplateSetMixin can't make a date object from the "
                        "self.template_set_date_attr attribute on self.object."
                    )
            else:
                raise ImproperlyConfigured(
                    "TemplateSetMixin can't find a {} attribute on self.object. "
                    "Either change self.template_set_date_attr or use a different "
                    "get_template_set_date() method."
                )
        else:
            raise ImproperlyConfigured(
                "TemplateSetMixin.get_template_set_date() assumes there is a "
                "self.object. Provide one or use a different "
                "get_template_set_date() method."
            )

    def get_template_names(self):
        """
        Like the standard get_template_names() methods, it returns an array of
        template names.

        If this page is within the dates of a template set, that set's template
        is first, followed by self.template.
        """
        templates = []

        if self.template_set is not None:
            templates.append("sets/{}/{}".format(self.template_set, self.template_name))

        if self.template_name is None:
            raise ImproperlyConfigured(
                "TemplateSetMixin requires a definition of 'template_name'"
            )
        else:
            templates.append(self.template_name)

        return templates

    def set_template_set(self):
        """
        Sets the value of self.template_set, if an appropriate template set is
        found.
        """
        if app_settings.TEMPLATE_SETS is not None:
            date = self.get_template_set_date()

            for ts in app_settings.TEMPLATE_SETS:
                start = make_date(ts["start"])
                end = make_date(ts["end"])
                if date >= start and date <= end:
                    self.template_set = ts["name"]
                    break


class TweetDetailRedirectView(RedirectView):
    """
    Redirecting URLs for an individual Tweet to the DayArchive page.

    Because if we click the 'View on site' link in Django Admin when
    viewing a Tweet it uses the Tweet.get_absolute_url() method
    in django-ditto. But we don't include the twitter URLs, and don't
    have a TweetDetail page in hines.

    So we've added a URL with the namespace:name of
    "twitter:tweet_detail" that points to here.

    And we redirect to the DayArchiveView with an #anchor of
    #tweet-{tweet_id}
    """

    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        twitter_id = kwargs.get("twitter_id", None)

        tweet = get_object_or_404(Tweet, twitter_id=twitter_id)

        url = reverse(
            "hines:day_archive",
            kwargs={
                "year": tweet.post_time.year,
                "month": tweet.post_time.month,
                "day": tweet.post_time.day,
            },
        )

        return f"{url}#tweet-{tweet.twitter_id}"


def timezone_today():
    """
    Return the current date in the current time zone.
    """
    if settings.USE_TZ:
        return timezone.localtime(timezone.now()).date()
    else:
        return datetime.date.today()


def _date_from_string(
    year, year_format, month="", month_format="", day="", day_format="", delim="__"
):
    """
    Helper: get a datetime.date object given a format string and a year,
    month, and day (only year is mandatory). Raise a 404 for an invalid date.

    Copied from https://github.com/django/django/blob/2.0/django/views/generic/dates.py#L609  # noqa: E501
    """
    format = year_format + delim + month_format + delim + day_format
    datestr = str(year) + delim + str(month) + delim + str(day)
    try:
        return datetime.datetime.strptime(datestr, format).date()
    except ValueError:
        raise Http404(
            _("Invalid date string '%(datestr)s' given format '%(format)s'")
            % {"datestr": datestr, "format": format}
        )
