import calendar
import datetime, time
from weblog.models import Blog, Entry, TaggedEntry
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db.models import Count
from django.shortcuts import get_list_or_404, get_object_or_404
from taggit.models import Tag
from shortcuts import render
from django.views.generic.date_based import archive_month, archive_year
from django.template import RequestContext
from django.db.models import Max, Min

    
def weblog_archive_month(request, blog_slug, year, month):
    """
    Wrapper for the archive_month Generic View, so we can make it blog-specific.
    Although the template gives us next_month and previous_month for free, these
    don't take into account whether there are actually Entries on those months.
    So we go to a lot of trouble here to check that and pass our own dates in.
    """
    blog = get_object_or_404(Blog, slug=blog_slug)
    queryset = Entry.live.filter( blog__slug__exact = blog.slug )
    
    # Get the date of the 1st of this month.
    date_stamp = time.strptime(year+month+'01', "%Y%m%d")
    first_of_month = datetime.date(*date_stamp[:3])
    
    # Get the most recent entry that is before the current month.
    prev_months_entry = Entry.live.filter(
        blog__slug__exact = blog.slug,
        published_date__lt = first_of_month,
    ).annotate(max_date=Max('published_date')).order_by('-max_date')[:1]
    
    previous_month_correct = prev_months_entry[0].published_date if prev_months_entry else None

    if first_of_month.month == datetime.datetime.now().month:
        # Current month, no need to look for Entries in next month.
        next_month_correct = None
    else:
        # Get the date of the 1st of next month.
        try:
            next_mon = first_of_month.replace(month=first_of_month.month+1)
        except ValueError:
            next_mon = first_of_month.replace(year=first_of_month.year+1, month=1)
    
        # Get the next entry that is after the current month.
        next_months_entry = Entry.live.filter(
            blog__slug__exact = blog.slug,
            published_date__gte = next_mon,
        ).annotate(max_date=Max('published_date')).order_by('max_date')[:1]
    
        next_month_correct = next_months_entry[0].published_date if next_months_entry else None
    
    return archive_month(request, year, month, queryset, 'published_date',
        template_object_name = 'entry',
        context_processors = [RequestContext,],
        month_format = '%m',
        extra_context = {
            'blog':blog,
            'previous_month_correct':previous_month_correct,
            'next_month_correct':next_month_correct,
        }
    )
    
    
def weblog_archive_year(request, blog_slug, year):
    """
    Wrapper for the archive_year Generic View, so we can make it blog-specific.
    Although the template tives us next_year and previous_year for free, these
    don't take into account whether there are actually Entries in those Years.
    So we go to a lot of trouble here to check that and pass our own dates in.
    """
    blog = get_object_or_404(Blog, slug=blog_slug)
    queryset = Entry.live.filter( blog__slug__exact = blog.slug )
    
    # Get the date of the 1st of this year.
    date_stamp = time.strptime(year+'0101', "%Y%m%d")
    first_of_year = datetime.date(*date_stamp[:3])
    
    # Get the most recent entry that is before the current year.
    prev_years_entry = Entry.live.filter(
        blog__slug__exact = blog.slug,
        published_date__lt = first_of_year,
    ).annotate(max_date=Max('published_date')).order_by('-max_date')[:1]

    previous_year_correct = prev_years_entry[0].published_date if prev_years_entry else None
    
    if first_of_year.year == datetime.datetime.now().year:
        # Current year, no need to look for Entries in next year.
        next_year_correct = None
    else:
        # Get the date of the 1st of next year.
        next_year = first_of_year.replace(year=first_of_year.year+1)
    
        # Get the next entry that is after the current year.
        next_years_entry = Entry.live.filter(
            blog__slug__exact = blog.slug,
            published_date__gte = next_year,
        ).annotate(max_date=Max('published_date')).order_by('max_date')[:1]
    
        next_year_correct = next_years_entry[0].published_date if next_years_entry else None

    return archive_year(request, year, queryset, 'published_date', 
        template_object_name = 'entry',
        context_processors = [RequestContext,],
        make_object_list = True,
        extra_context = {
            'blog':blog,
            'previous_year_correct':previous_year_correct,
            'next_year_correct':next_year_correct,
        }
    )


def weblog_blog_index(request, blog_slug):
    blog = get_object_or_404(Blog, slug=blog_slug)

    paginator = Paginator(Entry.live.filter(blog__slug__exact = blog_slug), 15, orphans=2)
    
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    
    # If page request (9999) is out of range, deliver last page of results.
    try:
        entries = paginator.page(page)
    except (EmptyPage, InvalidPage):
        entries = paginator.page(paginator.num_pages)
    
    # Get the most popular tags that are within this Blog, and that are on LIVE Entries.
    popular_tags = Tag.objects.filter(
        weblog_taggedentry_items__content_object__blog=blog,
        weblog_taggedentry_items__content_object__status=Entry.LIVE_STATUS,
    ).annotate(num_times=Count('weblog_taggedentry_items')).order_by('-num_times')[:15]
     
    featured_entries = Entry.featured_set.all()
    
    return render(request, 'weblog/index.html', {
        'blog': blog,
        'entries': entries,
        'popular_tags': popular_tags,
        'featured_entries': featured_entries,
    })


def weblog_entry_detail(request, blog_slug, year, month, day, slug):
    
    date_stamp = time.strptime(year+month+day, "%Y%m%d")
    published_date = datetime.date(*date_stamp[:3])
    
    entry = get_object_or_404(Entry.live.all(),
                                blog__slug__exact = blog_slug,
                                published_date__year = published_date.year,
                                published_date__month = published_date.month,
                                published_date__day = published_date.day,
                                slug=slug,
                            )

    other_blogs = Blog.objects.with_entries(
        entry_filter={
            'published_date__year' : published_date.year,
            'published_date__month' : published_date.month,
            'published_date__day' : published_date.day,
        },
        entry_exclude={
            'pk' : entry.pk
        }
    )
    
    return render(request, 'weblog/entry_detail.html', {
       'blog': entry.blog,
       'entry': entry,
       'other_blogs': other_blogs,
    })


def weblog_blog_archive(request, blog_slug):
    blog = get_object_or_404(Blog, slug=blog_slug)
    
    monthly_dates = Entry.live.filter(blog__slug__exact = blog_slug).dates('published_date', 'month', order='ASC')
    
    years = []
    months = []
    prev_year = ''
    for month_date in monthly_dates:
        if month_date.year != prev_year:
            if months:
                years.append(months)
                months = []
            prev_year = month_date.year
        months.append(month_date)
    years.append(months)

    return render(request, 'weblog/archive.html', {
        'blog': blog,
        'years': years,
    })


def weblog_tag(request, blog_slug, tag_slug):
    blog = get_object_or_404(Blog, slug=blog_slug)
    tag = get_object_or_404(Tag, slug=tag_slug)
    
    entries = list(Entry.live.filter(
                                blog = blog,
                                tags__name__in=[tag.slug]
                            ))
    
    return render(request, 'weblog/tag.html', {
        'blog': blog,
        'tag': tag,
        'entries': entries,
    })
