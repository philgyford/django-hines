import datetime

from dal import autocomplete
from taggit.models import Tag

from django.conf import settings
from django.http import Http404
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.translation import ugettext as _
from django.views.generic import DateDetailView, DetailView,\
        ListView, MonthArchiveView, RedirectView, YearArchiveView
from django.views.generic.detail import SingleObjectMixin

from hines.core.views import TemplateSetMixin
from .models import Blog, Post


# Colorful
# http://web.archive.org/web/20000819162919/http://www.gyford.com:80/phil/daily/
# 2000-03-01 - 2000-12-31

# Monochrome
# http://web.archive.org/web/20010214232232/http://www.gyford.com:80/phil/writing/
# 2001-01-01 - 2002-11-09

# Blue links
# http://web.archive.org/web/20021211042734/http://www.gyford.com:80/phil/writing/2002/11/11/000072.php
# 2002-11-10 - 2006-03-15

# The basis for how it still is
# http://web.archive.org/web/20060323001155/http://www.gyford.com/phil/writing/2006/03/16/my_new_site.php
# 2006-03-16 - 2006-08-29

# Sight & Sound
# http://web.archive.org/web/20071011030825/http://www.gyford.com/phil/writing/2006/08/30/a_lick_of_paint.php
# 2006-08-30 - 2009-02-09

# A bit wider
# http://web.archive.org/web/20090227031141/http://www.gyford.com/phil/writing/2009/02/10/front_page.php
# 2009-02-10 - now


class BlogDetailParentView(SingleObjectMixin, ListView):
    """
    A parent class for all views that will list Posts from a Blog.
    """
    slug_url_kwarg = 'blog_slug'
    paginate_by = 25
    page_kwarg = 'p'
    allow_empty = False

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Blog.objects.all())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blog'] = self.object
        context['post_list'] = context['object_list']
        return context


class BlogDetailView(BlogDetailParentView):
    "Front page of a Blog, listing its recent Posts."
    template_name = 'weblogs/blog_detail.html'

    def get_queryset(self):
        return self.object.public_posts.all()


class BlogArchiveView(DetailView):
    "List of all the months in which there are posts."
    template_name = 'weblogs/blog_archive.html'
    model = Blog
    slug_url_kwarg = 'blog_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['months'] = self.get_months()
        return context

    def get_months(self):
        return self.object.public_posts.dates('time_created', 'month')


class BlogTagDetailView(BlogDetailParentView):
    "Listing Posts with a particular Tag (by 'tag_slug') in a Blog."
    template_name = 'weblogs/blog_tag_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = Tag.objects.get(slug=self.kwargs.get('tag_slug'))
        return context

    def get_queryset(self):
        return self.object.public_posts.filter(
                                tags__slug__in=[self.kwargs.get('tag_slug')])


class BlogTagListView(DetailView):
    "Listing the most popular Tags in a Blog."
    model = Blog
    slug_url_kwarg = 'blog_slug'
    template_name = 'weblogs/blog_tag_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag_list'] = self.object.popular_tags(num=30)
        return context


class PostDetailView(TemplateSetMixin, DateDetailView):
    """
    A bit complicated because we need to match the post using its slug,
    its date, and its weblog slug.
    """
    date_field = 'time_published'
    model = Post
    month_format = '%m'
    slug_url_kwarg = 'post_slug'
    # The default, unless we have a different template set to use for this
    # Post's date:
    template_name = 'weblogs/post_detail.html'

    # Not a standard field, but we'll store the date here.
    date = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object:
            context['blog'] = self.object.blog

            if self.object.status != Post.LIVE_STATUS:
                context['is_preview'] = True

        return context

    def get_date(self):
        """
        Not a standard method but we need to do this in a couple of places.
        """
        if self.date is None:
            year = self.get_year()
            month = self.get_month()
            day = self.get_day()
            self.date = _date_from_string(year, self.get_year_format(),
                                         month, self.get_month_format(),
                                         day, self.get_day_format())
        return self.date

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

        date = self.get_date()
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

    def get_template_set_date(self):
        return self.get_date()

    def get_queryset(self):
        """
        Allow a Superuser to see draft Posts.
        Everyone else can only see public Posts.
        """
        if self.request.user.is_superuser:
            return self.model.objects.all()
        else:
            return self.model.public_objects.all()


class PostDatedArchiveMixin(object):
    """
    A mixin for the month/year archive views that restricts results to a
    Blog defined by the `blog_slug` URL kwarg.
    Also includes `blog` in the context_data.
    """
    allow_empty = False
    allow_future = False
    date_field = 'time_published'
    model = Post
    queryset = Post.public_objects

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(blog__slug=self.kwargs.get('blog_slug'))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['blog'] = Blog.objects.get(
                                            slug=self.kwargs.get('blog_slug'))
        except Blog.DoesNotExist:
            context['blog'] = None
        return context


class PostDayArchiveView(RedirectView):
    """
    To keep things simple we redirect to the overall day view.
    """
    def get_redirect_url(self, *args, **kwargs):
        return reverse('hines:day_archive', kwargs={
            'year': kwargs['year'],
            'month':kwargs['month'],
            'day':  kwargs['day']
        })


class PostMonthArchiveView(PostDatedArchiveMixin, MonthArchiveView):
    month_format = '%m'
    template_name = 'weblogs/post_archive_month.html'


class PostYearArchiveView(PostDatedArchiveMixin, YearArchiveView):
    year_format = '%Y'
    make_object_list = True
    template_name = 'weblogs/post_archive_year.html'


class PostTagAutocomplete(autocomplete.Select2QuerySetView):
    """
    Used to autocomplete tag suggestions in the Admin Post change view.
    Using django-autocomplete-light.
    """
    def get_queryset(self):
        if not self.request.user.is_authenticated():
            raise Http404("Not found")

        qs = Tag.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q).order_by('name')

        return qs


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
