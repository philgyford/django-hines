import datetime
import random

from dal import autocomplete
from taggit.models import Tag
from markdownx.views import ImageUploadView

from django.http import Http404, JsonResponse
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.views.generic import DateDetailView, DetailView,\
        ListView, MonthArchiveView, RedirectView, TemplateView, YearArchiveView
from django.views.generic.detail import SingleObjectMixin

from hines.core.views import PaginatedListView, TemplateSetMixin
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


class BlogDetailParentView(SingleObjectMixin, PaginatedListView):
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
        context['tag_list'] = self.object.popular_tags(num=100)
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


class PostRedirectView(RedirectView):
    """
    Redirect from old Movable Type URLs.
    Remove the '.php'.
    Replace any underscores with hyphens.
    """
    def get_redirect_url(self, blog_slug, year, month, day, post_slug):
        post_slug = post_slug.replace('_', '-')
        return reverse('weblogs:post_detail', kwargs={
            'blog_slug': blog_slug,
            'year': year, 'month': month, 'day': day,
            'post_slug': post_slug, })


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
        if not self.request.user.is_authenticated:
            raise Http404("Not found")

        qs = Tag.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q).order_by('name')

        return qs


# Generating errors:
# https://github.com/neutronX/django-markdownx/issues/101
# So not using this for the moment.
#
# class PostImageUploadView(ImageUploadView):
    # """
    # Just replacing the form_valid() method so we can provide our own HTML.

    # Based on https://github.com/neutronX/django-markdownx/blob/master/markdownx/views.py#L55
    # """
    # def form_valid(self, form):
        # """
        # If the form is valid, the contents are saved.
        # If the **POST** request is AJAX (image uploads), a JSON response will be
        # produced containing the Markdown encoded image insertion tag with the URL
        # using which the uploaded image may be accessed.
        # JSON response would be as follows:
        # .. code-block:: bash
            # { image_code: "![](/media/image_directory/123-4e6-ga3.png)" }
        # :param form: Django form instance.
        # :type form: django.forms.Form
        # :return: JSON encoded Markdown tag for AJAX requests, and an appropriate
                 # response for HTTP requests.
        # :rtype: django.http.JsonResponse, django.http.HttpResponse
        # """
        # response = super().form_valid(form)

        # if self.request.is_ajax():
            # image_path = form.save(commit=True)
            # image_code = '![]({})'.format(image_path)
            # # image_code = """<figure class="figure figure--img figure--full">
  # # <a href="{}" title="See larger version"><img src="{}" alt=""></a>
# # </figure>
# # """.format(image_path, image_path)
            # return JsonResponse({'image_code': image_code})

        # return response


class RandomPhilView(TemplateView):
    """
    Replicating an old /cgi-bin/random_phil.cgi script.

    If sets='2002' is passed into the view, we use the 2002 template set.
    Otherwise the default is the 2001 (generally displayed in a little pop-up window).

    GET: Display a random photo, getting its data from the photos array.

    POST: The form submits an `idx` field which is a string of photo indexes
    like "4+2+17". We display a photo whose index is not in that string. And
    we add this photo's index to that string for next time. When all the
    photos have been used `idx` is set back to empty and it starts again.
    """
    template_name = 'sets/2001/weblogs/random_phil.html'
    http_method_names = ['get', 'post',]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update( self.get_random_phil() )
        return context

    def post(self, request, *args, **kwargs):
        "The image form has been submitted. Get another image."
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_template_names(self):
        "Use the 2002 template, or the default 2001?"
        if self.kwargs.get('set', False) == '2002':
            return ['sets/2002/weblogs/random_phil.html',]
        else:
            return [self.template_name,]

    def get_random_phil(self):
        """
        Returns a dict of stuff for context_data.

        Looks for an `idx` POST argument, which is a string of numbers in
        the format '1+5+12+3'.

        This is all a bit nasty but was adapted from a 2001-era perl cgi
        script so.

        The returned dict has these elements:

        'idx1': An int, the 1-based number of the image. 1 the first time an
                image is displayed. 2 when the user requests the next. Then 3,
                etc.
        'idx_list': A list of all the 0-based indexes of the images already
                    displayed, including the current one. Indexes based on
                    the `photos` list, not the order in which they were
                    displayed to the user. The list is a string like '1+5+12+3'.
        'total_images': An int, the total number of photos there are to display.
        'image': A dict of data about the image to display. Pulled directly
                 from the `photos` list.
        """
        photos = [
            {
                "file":    "stuart_1998.jpg",
                "width":    "200",
                "height":    "207",
                "credit":    "Stuart",
                "url":    "http://www.subatomic.com/",
                "caption":    "London, 1998.",
            },
            {
                "file":    "nick_1999.jpg",
                "width":    "200",
                "height":    "255",
                "credit":    "Nick",
                "url":    "http://if.only.org/",
                "caption":    "Amsterdam, 1999.",
            },
            {
                "file":    "sam_1999.jpg",
                "width":    "235",
                "height":    "200",
                "credit":    "Sam",
                "url":    "http://www.haddock.org/directory/society/haddocks/samurquhart/",
                "caption":    "Me and Sam, Amsterdam, 1999.",
            },
            {
                "file":    "mia_2000.jpg",
                "width":    "200",
                "height":    "200",
                "credit":    "",
                "url":    "",
                "caption":    "<a href='http://www.geocities.com/sorgim/' target='opener'>Mia</a> and me, New York, 2000.",
            },
            {
                "file":    "chippinghill_small.jpg",
                "width":    "258",
                "height":    "212",
                "credit":    "<cite>Witham and Braintree Times</cite>",
                "url":    "",
                "caption":    "At school, mid-1970s.",
            },
            {
                "file":    "bryan_2000.jpg",
                "width":    "180",
                "height":    "273",
                "credit":    "Bryan",
                "url":    "http://www.bryanboyer.com/",
                "caption":    "Austin, Texas, 2000.",
            },
            {
                "file":    "brad_2000.jpg",
                "width":    "173",
                "height":    "208",
                "credit":    "Brad",
                "url":    "http://www.bradlands.com/",
                "caption":    "Austin, Texas, 2000.",
            },
            {
                "file":    "connected_1997.jpg",
                "width":    "202",
                "height":    "260",
                "credit":    "",
                "url":    "",
                "caption":    "<cite>Daily Telegraph</cite>, 1997.",
            },
            {
                "file":    "des_1998.jpg",
                "width":    "240",
                "height":    "205",
                "credit":    "Des",
                "url":    "http://www.kfs.org/~desiree/",
                "caption":    "Stef and me, London, 1998.",
            },
            {
                "file":    "mac_1997.jpg",
                "width":    "250",
                "height":    "189",
                "credit":    "Mac",
                "url":    "http://www.incline.co.uk/mac/",
                "caption":    "A bad mood, London, 1997.",
            },
            {
                "file":    "pouneh_2000.jpg",
                "width":    "180",
                "height":    "213",
                "credit":    "Pouneh",
                "url":    "",
                "caption":    "San Francisco, 2000.",
            },
            {
                "file":    "janelle_2000.jpg",
                "width":    "185",
                "height":    "205",
                "credit":    "Janelle",
                "url":    "http://www.salon.com/directory/topics/janelle_brown/",
                "caption":    "San Francisco, 2000.",
            },
            {
                "file":    "peter_2000.jpg",
                "width":    "200",
                "height":    "184",
                "credit":    "Peter",
                "url":    "http://www.peterme.com/",
                "caption":    "San Francisco, 2000.",
            },
            {
                "file":    "andy_2000.jpg",
                "width":    "180",
                "height":    "252",
                "credit":    "Andy",
                "url":    "",
                "caption":    "Beaconsfield, 2000.",
            },
            {
                "file":    "mattj_2000.jpg",
                "width":    "200",
                "height":    "231",
                "credit":    "Matt J",
                "url":    "http://www.blackbeltjones.com/",
                "caption":    "London, 2000.",
            },
            {
                "file":    "mattl_2000.jpg",
                "width":    "180",
                "height":    "231",
                "credit":    "Matt L",
                "url":    "",
                "caption":    "Fingers by <a href='http://if.only.org/' target='opener'>Nick</a>, London, 2000.",
            },
            {
                "file":    "bryan_2001.jpg",
                "width":    "260",
                "height":    "183",
                "credit":    "Bryan",
                "url":    "http://www.bryanboyer.com/",
                "caption":    "<a href='http://www.blackbeltjones.com/' target='opener'>Matt</a> and me, London, 2001",
            },
            {
                "file":    "james_2001.jpg",
                "width":    "200",
                "height":    "206",
                "credit":    "James",
                "url":    "",
                "caption":    "Burning Man, 2001",
            },
            {
                "file":    "kay_2001.jpg",
                "width":    "191",
                "height":    "191",
                "credit":    "Kay",
                "url":    "",
                "caption":    "Burning Man, 2001",
            },
            {
                "file":    "yoz_20011121.jpg",
                "width":    "220",
                "height":    "250",
                "credit":    "Yoz",
                "url":    "http://www.yoz.com/",
                "caption":    "Me and Alice, London, 2001",
            },
            {
                "file":    "mary_2002062201.jpg",
                "width":    "172",
                "height":    "250",
                "credit":    "Mary",
                "url":    "http://www.sparklytrainers.com/",
                "caption":    "Grays, Essex, 2002",
            },
            {
                "file":    "mary_2002062202.jpg",
                "width":    "184",
                "height":    "260",
                "credit":    "Mary",
                "url":    "http://www.sparklytrainers.com/",
                "caption":    "Grays, Essex, 2002",
            },
            {
                "file":    "yoz_20020227.jpg",
                "width":    "199",
                "height":    "240",
                "credit":    "Yoz",
                "url":    "http://www.yoz.com/",
                "caption":    "Me and Mary, London, 2002",
            }
        ]

        # Was a string containing a list of indexes submitted?
        idx_list = self.request.POST.get('idx', '')
        if idx_list == '':
            used_pics = []
        else:
            # Will be like ['3', '15', '0']:
            used_pics = idx_list.split('+')

        if len(used_pics) > 0:
            # This isn't the first time here, so find a new photo.

            if len(used_pics) == len(photos):
                # We've now used all the pics, so start again.
                new_idx = random.randint(0, len(photos) - 1)
                used_pics = []
            else:
                new_idx = used_pics[0]
                while str(new_idx) in used_pics:
                    new_idx = random.randint(0, len(photos) - 1)

        else:
            # This is the first time here so find any old random pic.
            new_idx = random.randint(0, len(photos) - 1)

        used_pics.append(str(new_idx))

        return {
            'idx1': len(used_pics),
            'idx_list': ('+').join(used_pics),
            'total_images': len(photos),
            'image': photos[new_idx],
        }


def _date_from_string(year, year_format, month='', month_format='', day='', day_format='', delim='__'):
    """
    Helper: get a datetime.date object given a format string and a year,
    month, and day (only year is mandatory). Raise a 404 for an invalid date.

    Copied from https://github.com/django/django/blob/2.0/django/views/generic/dates.py#L609
    """
    format = year_format + delim + month_format + delim + day_format
    datestr = str(year) + delim + str(month) + delim + str(day)
    try:
        return datetime.datetime.strptime(datestr, format).date()
    except ValueError:
        raise Http404(_("Invalid date string '%(datestr)s' given format '%(format)s'") % {
            'datestr': datestr,
            'format': format,
        })
