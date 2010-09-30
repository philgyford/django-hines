import datetime, time
from weblog.models import Blog, Entry
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import get_list_or_404, get_object_or_404
from taggit.models import Tag
from shortcuts import render


def weblog_archive_month(request, blog_slug, year, month):
    blog = get_object_or_404(Blog, slug=blog_slug)
    date_stamp = time.strptime(year+month+'01', "%Y%m%d")
    published_date = datetime.date(*date_stamp[:3])
    entries = list(Entry.live.filter(
                                blog__slug__exact = blog_slug,
                                published_date__year = published_date.year,
                                published_date__month = published_date.month,
                            ))
    
    return render(request, 'weblog/entry_archive_month.html', {
        'blog': blog,
        'entries': entries,
        'date': published_date,
    })
    
def weblog_archive_year(request, blog_slug, year):
    blog = get_object_or_404(Blog, slug=blog_slug)
    date_stamp = time.strptime(year+'0101', "%Y%m%d")
    published_date = datetime.date(*date_stamp[:3])
    entries = list(Entry.live.filter(
                                blog__slug__exact = blog_slug,
                                published_date__year = published_date.year,
                            ))
    
    return render(request, 'weblog/entry_archive_year.html', {
        'blog': blog,
        'entries': entries,
        'date': published_date,
    })

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
    
    popular_tags = Entry.tags.most_common()[:15]
    
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
                                blog__slug__exact = blog.slug,
                                tags__name__in=[tag.slug]
                            ))
    
    return render(request, 'weblog/tag.html', {
        'blog': blog,
        'tag': tag,
        'entries': entries,
    })
