import datetime

from django.conf import settings
from django.http import Http404
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.translation import ugettext as _
from django.views.generic import ListView, TemplateView
from django.views.generic.dates import DayMixin, MonthMixin, YearMixin

from ditto.flickr.models import Photo, Photoset
from ditto.pinboard.models import Bookmark
from ditto.twitter.models import Tweet
from hines.weblogs.models import Blog, Post
from .paginator import DiggPaginator


class HomeView(TemplateView):
    template_name = 'hines_core/home.html'


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

        context.update(object_lists)

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

        object_lists.update(self._get_weblog_posts(date))

        object_lists.update(self._get_flickr_photos(date))

        object_lists.update(self._get_pinboard_bookmarks(date))

        object_lists.update(self._get_twitter_favorites(date))

        object_lists.update(self._get_twitter_tweets(date))

        if not allow_empty:
            if len(object_lists) == 0:
                raise Http404(_("Nothing available"))

        return (None, object_lists, {
            'day': date,
            'previous_day': self.get_previous_day(date),
            'next_day': self.get_next_day(date),
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
        Returns a dict with key 'blogs'.
        The value is a list of dicts:
            {
                'blogs': [
                    {
                        'blog': BlogObject,
                        'post_list': Post.objects...,
                    }
                ]
            }
        """
        blogs = []
        for blog in Blog.objects.all():
            qs = blog.public_posts.filter(time_published__date=date)
            if qs.count() > 0:
                blogs.append({
                    'blog': blog,
                    'post_list': qs
                })

        if len(blogs) > 0:
            return {'blogs': blogs}
        else:
            return {}

    def _get_flickr_photos(self, date):
        photos = Photo.public_objects.filter(
                                        taken_time__date=date,
                                        taken_granularity=0)
        if photos.count() > 0:
            return {'flickr_photo_list': photos, }
        else:
            return {}

    def _get_pinboard_bookmarks(self, date):
        bookmarks = Bookmark.public_objects.filter(post_time__date=date)
        if bookmarks.count() > 0:
            return {'pinboard_bookmark_list': bookmarks, }
        else:
            return {}

    def _get_twitter_favorites(self, date):
        tweets = Tweet.public_favorite_objects.filter(post_time__date=date) \
                                                    .prefetch_related('user')
        if tweets.count() > 0:
            return {'twitter_favorite_list': tweets, }
        else:
            return {}

    def _get_twitter_tweets(self, date):
        tweets = Tweet.public_tweet_objects.filter(post_time__date=date) \
                                                    .prefetch_related('user')
        if tweets.count() > 0:
            return {'twitter_tweet_list': tweets, }
        else:
            return {}


class PaginatedListView(ListView):
    """Use this instead of ListView to provide standardised pagination."""
    paginator_class = DiggPaginator
    paginate_by = 50
    page_kwarg = 'p'

    # See ditto.core.paginator for what these mean:
    paginator_body = 5
    paginator_margin = 2
    paginator_padding = 2
    paginator_tail = 2

    def __init__(self, **kwargs):
        return super().__init__(**kwargs)

    def paginate_queryset(self, queryset, page_size):
        """
        Paginate the queryset, if needed.

        This is EXACTLY the same as the standard ListView.paginate_queryset()
        except for this line:
            page = paginator.page(page_number, softlimit=True)
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
            page = paginator.page(page_number, softlimit=True)
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
