import datetime

from django.conf import settings
from django.http import Http404
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView
from django.views.generic.dates import DayMixin, MonthMixin, YearMixin


class HomeView(TemplateView):
    template_name = 'core/home.html'


class DayArchiveView(YearMixin, MonthMixin, DayMixin, TemplateView):
    """
    Trying to keep things a bit consistent with BaseDateListView, except we
    don't have a single QuerySet we're fetching for this date, so we can't
    use it.
    """
    allow_future = False
    day_format = '%d'
    month_format = '%m'
    year_format = '%Y'
    template_name = 'core/archive_day.html'

    def get_allow_future(self):
        """
        Returns `True` if the view should be allowed to display objects from
        the future.
        """
        return self.allow_future

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # date_list and object_list aren't used here.
        date_list, object_list, extra_context = self.get_dated_items()
        context.update(extra_context)
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
        """
        return (None, None, {
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

    def get_previous_day(self, date):
        return date - datetime.timedelta(days=1)


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
