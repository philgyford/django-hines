from collections import OrderedDict
import datetime

from django.conf import settings
from django.core.paginator import InvalidPage
from django.http import Http404
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.translation import ugettext as _
from django.views.generic import ListView, TemplateView
from django.views.generic.dates import DayMixin, MonthMixin, YearMixin

from ditto.flickr.models import Photo, Photoset
from ditto.pinboard.models import Bookmark
from ditto.twitter.models import Tweet
from hines.core.utils import make_date
from hines.weblogs.models import Blog, Post
from .paginator import DiggPaginator


class HomeView(TemplateView):
    template_name = 'hines_core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sections'] = self.get_recent_items()
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
            items.update({blog:posts})
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
                if hasattr(qs[0], 'time_published'):
                    return qs[0].time_published
                else:
                    return qs[0].post_time
            return False

        # Sort the dict of items so that they're in reverse-chronological
        # order, based on their most recent post, photo, link etc.
        sorted_items = OrderedDict(
                    sorted(items.items(), key=by_time_key, reverse=True))

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

        if hasattr(settings, 'HINES_HOME_PAGE_DISPLAY'):
            if section_name in settings.HINES_HOME_PAGE_DISPLAY:
                section_quantity = settings.HINES_HOME_PAGE_DISPLAY[section_name]
                if section_name == 'weblog_posts':
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
            quantity = self._get_section_quantity('weblog_posts', blog.slug)
            if quantity > 0:
                qs = blog.public_posts.all()[:quantity]
            key = 'weblog_posts_{}'.format(blog.slug)
            posts[key] = qs

        return posts

    def _get_flickr_photos(self):
        quantity = self._get_section_quantity('flickr_photos')
        if quantity > 0:
            photos = Photo.public_objects.all()[:quantity]
        else:
            photos = Photo.objects.none()
        return {'flickr_photo_list': photos}

    def _get_pinboard_bookmarks(self):
        quantity = self._get_section_quantity('pinboard_bookmarks')
        if quantity > 0:
            bookmarks = Bookmark.public_objects.all()[:quantity]
        else:
            bookmarks = Bookmar.objects.none()
        return {'pinboard_bookmark_list': bookmarks}


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
    day_format = '%d'
    month_format = '%m'
    year_format = '%Y'
    template_name = 'hines_core/archive_day.html'

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

        context['sections'] = object_lists

        return context

    def get_dated_items(self):
        """
        Return (date_list, items, extra_context) for this request.
        (Although date_list and items will be None.)
        """
        year = self.get_year()
        month = self.get_month()
        day = self.get_day()

        date = _date_from_string(year, self.get_year_format(),
                                 month, self.get_month_format(),
                                 day, self.get_day_format())

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
            object_lists.update({blog:posts})

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

        return (None, object_lists, {
            'day': date,
            'previous_day': self.get_previous_day(date),
            'next_day': self.get_next_day(date),
            'object_count': object_count,
        })

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
        if hasattr(settings, 'HINES_FIRST_DATE'):
            return datetime.datetime.strptime(
                                settings.HINES_FIRST_DATE, "%Y-%m-%d").date()
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
            key = 'weblog_posts_{}'.format(blog.slug)
            posts[key] = qs

        return posts

    def _get_flickr_photos(self, date):
        photos = Photo.public_objects.filter(
                                        taken_time__date=date,
                                        taken_granularity=0)
        return {'flickr_photo_list': photos}

    def _get_pinboard_bookmarks(self, date):
        bookmarks = Bookmark.public_objects.filter(post_time__date=date)
        return {'pinboard_bookmark_list': bookmarks}

    def _get_twitter_favorites(self, date):
        tweets = Tweet.public_favorite_objects.filter(post_time__date=date) \
                                                    .prefetch_related('user')
        return {'twitter_favorite_list': tweets}

    def _get_twitter_tweets(self, date):
        tweets = Tweet.public_tweet_objects.filter(post_time__date=date) \
                                                    .prefetch_related('user')
        return {'twitter_tweet_list': tweets}


class PaginatedListView(ListView):
    """Use this instead of ListView to provide standardised pagination."""
    paginator_class = DiggPaginator
    paginate_by = 30
    page_kwarg = 'p'
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
            orphans = self.get_paginate_orphans(),
            allow_empty_first_page = self.get_allow_empty(),
            body    = self.paginator_body,
            margin  = self.paginator_margin,
            padding = self.paginator_padding,
            tail    = self.paginator_tail,
        )
        page_kwarg = self.page_kwarg
        page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
        try:
            page_number = int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                raise Http404(_("Page is not 'last', nor can it be converted to an int."))
        try:
            page = paginator.page(page_number, softlimit=self.softlimit)
            return (paginator, page, page.object_list, page.has_other_pages())
        except InvalidPage as e:
            raise Http404(_('Invalid page (%(page_number)s): %(message)s') % {
                'page_number': page_number,
                'message': str(e)
            })


class PhotosHomeView(PaginatedListView):
    """
    We only have a single page showing photos, so doesn't make sense to put
    it in its own app. So here we are.
    """
    template_name = 'hines_core/photos_home.html'
    queryset = Photo.public_objects.all()
    # Divisible by three columns:
    paginate_by = 48

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['photoset_list'] = Photoset.objects.all() \
                                            .order_by('-last_update_time')[:10]

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
    template_set_date_attr = 'time_created'

    # Will be set to the name of the appropriate template set, if any.
    template_set = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Not sure this is the best place for this call...
        self.set_template_set()

        context['template_set'] = self.template_set

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
                    raise ImproperlyConfigure(
                        "TemplateSetMixin can't make a date object from the "
                        "self.template_set_date_attr attribute on self.object.")
            else:
                raise ImproperlyConfigured(
                "TemplateSetMixin can't find a {} attribute on self.object. "
                "Either change self.template_set_date_attr or use a different "
                "get_template_set_date() method.")
        else:
            raise ImproperlyConfigured(
                "TemplateSetMixin.get_template_set_date() assumes there is a "
                "self.object. Provide one or use a different "
                "get_template_set_date() method.")

    def get_template_names(self):
        """
        Like the standard get_template_names() methods, it returns an array of
        template names.

        If this page is within the dates of a template set, that set's template
        is first, followed by self.template.
        """
        templates = []

        if self.template_set is not None:
            templates.append(
                        'sets/{}/{}'.format(self.template_set,
                                            self.template_name))

        if self.template_name is None:
            raise ImproperlyConfigured(
                "TemplateSetMixin requires a definition of 'template_name'")
        else:
            templates.append(self.template_name)

        return templates

    def set_template_set(self):
        """
        Sets the value of self.template_set, if an appropriate template set is
        found.
        """
        if getattr(settings, 'HINES_TEMPLATE_SETS', None):
            date = self.get_template_set_date()

            for ts in settings.HINES_TEMPLATE_SETS:
                start = make_date(ts['start'])
                end = make_date(ts['end'])
                if date >= start and date <= end:
                    self.template_set = ts['name']
                    break



def timezone_today():
    """
    Return the current date in the current time zone.
    """
    if settings.USE_TZ:
        return timezone.localtime(timezone.now()).date()
    else:
        return datetime.date.today()

def _date_from_string(year, year_format, month='', month_format='', day='', day_format='', delim='__'):
    """
    Helper: get a datetime.date object given a format string and a year,
    month, and day (only year is mandatory). Raise a 404 for an invalid date.
    """
    format = delim.join((year_format, month_format, day_format))
    datestr = delim.join((year, month, day))
    try:
        return datetime.datetime.strptime(force_str(datestr), format).date()
    except ValueError:
        raise Http404(_("Invalid date string '%(datestr)s' given format '%(format)s'") % {
            'datestr': datestr,
            'format': format,
        })
