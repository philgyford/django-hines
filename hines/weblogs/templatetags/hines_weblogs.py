from django import template

from taggit.models import Tag

from ..models import Blog, Post


register = template.Library()


@register.simple_tag
def get_all_blogs():
    """
    Returns a QuerySet of Blog objects.
    """
    return Blog.objects.all()


@register.simple_tag
def get_all_blogs_by_slug():
    """
    Returns a dict of all Blog objects, with their slugs as the dict keys.
    """
    blogs = {}
    for blog in Blog.objects.all():
        blogs[blog.slug] = blog
    return blogs


@register.simple_tag
def recent_posts(blog, num=5):
    """
    Returns a QuerySet of `num` recently-published Posts for `blog`.
    """
    return blog.public_posts.all().order_by('-time_published')[:num]


@register.inclusion_tag('weblogs/includes/card_posts.html')
def recent_posts_card(blog, num=5):
    """
    Displays `num` recently-published Posts for `blog`.
    """
    return {
            'card_title': 'Recent posts',
            'post_list': recent_posts(blog=blog, num=num),
            }


@register.simple_tag
def blog_years(blog):
    """
    Returns a QuerySet of dates, one per year this blog has published Posts in.
    `blog` is a Blog object.
    """
    return Post.public_objects.filter(blog=blog).dates('time_published', 'year')


@register.inclusion_tag('weblogs/includes/card_years.html')
def blog_years_card(blog, current_year=None):
    """
    Displays the years this blog has published posts in.
    `blog` is a Blog object.
    `current_year` is the year (a date object) that shouldn't be a link, if any.
    """
    return {
            'card_title': 'Years of {}'.format(blog.short_name),
            'date_list': blog_years(blog=blog),
            'blog': blog,
            'current_year': current_year,
            }


@register.simple_tag
def blog_popular_tags(blog, num=10):
    """
    Returns a QuerySet of Tags, in descending order of popularity within
    `blog`.
    Each one has a `post_count` field indicating the number of Posts in this
    Blog that has this Tag.
    """
    return blog.popular_tags(num=num)


@register.inclusion_tag('weblogs/includes/card_tags.html')
def blog_popular_tags_card(blog, num=10):
    """
    """
    return {
            'card_title': 'Most-used tags',
            'tag_list': blog_popular_tags(blog=blog, num=num),
            'blog': blog,
            }

