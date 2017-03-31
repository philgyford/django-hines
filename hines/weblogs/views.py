import datetime

from django.http import Http404
from django.utils.encoding import force_str
from django.utils.translation import ugettext as _
from django.views.generic import DateDetailView, ListView
from django.views.generic.detail import SingleObjectMixin

from .models import Blog, Post


class BlogDetailView(SingleObjectMixin, ListView):
    slug_url_kwarg = 'blog_slug'
    template_name = "weblogs/blog_detail.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Blog.objects.all())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blog'] = self.object
        context['post_list'] = context['object_list']
        return context

    def get_queryset(self):
        return self.object.posts.all()


class PostDetailView(DateDetailView):
    date_field = 'time_published'
    model = Post
    month_format = '%m'
    slug_url_kwarg = 'post_slug'
    template_name = "weblogs/post_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object:
            context['blog'] = self.object.blog
        return context

    def get_object(self, queryset=None):
        """
        Returns the object the view is displaying.
        This is our custom version where:
            * We know we're using the post's slug, not a pk.
            * And we require the correct blog slug.
            * And we need the correct date parts.

        This replaces both BaseDateDetailView.get_object() and
        SingleObjectMixin.get_object().
        """
        if queryset is None:
            queryset = self.get_queryset()

        year = self.get_year()
        month = self.get_month()
        day = self.get_day()
        date = _date_from_string(year, self.get_year_format(),
                                 month, self.get_month_format(),
                                 day, self.get_day_format())
        blog_slug = self.kwargs.get('blog_slug')
        post_slug = self.kwargs.get(self.slug_url_kwarg)

        if not self.get_allow_future() and date > datetime.date.today():
            raise Http404(_(
                "Future %(verbose_name_plural)s not available because "
                "%(class_name)s.allow_future is False."
            ) % {
                'verbose_name_plural': qs.model._meta.verbose_name_plural,
                'class_name': self.__class__.__name__,
            })

        # Filter down a queryset from self.queryset using the date from the
        # URL. This'll get passed as the queryset to DetailView.get_object,
        # which'll handle the 404
        lookup_kwargs = self._make_single_date_lookup(date)

        queryset = queryset.filter(**lookup_kwargs)

        if blog_slug is not None and post_slug is not None:
            blog_slug_field = 'blog__slug'
            post_slug_field = self.get_slug_field()
            queryset = queryset.filter(**{
                                            blog_slug_field: blog_slug,
                                            post_slug_field: post_slug
                                        })
        else:
            raise AttributeError("PostDetailView must be called with "
                                 "a blog slug and a post slug.")
        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(_("No Posts found matching the query"))
        return obj


def _date_from_string(year, year_format, month='', month_format='', day='', day_format='', delim='__'):
    """
    Helper: get a datetime.date object given a format string and a year,
    month, and day (only year is mandatory). Raise a 404 for an invalid date.

    Copied from https://github.com/django/django/blob/1.10/django/views/generic/dates.py
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
