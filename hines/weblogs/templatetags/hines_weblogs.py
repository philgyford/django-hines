from django import template

from ..models import Post


register = template.Library()


@register.assignment_tag
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


@register.assignment_tag
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
            'card_title': 'Years of {}'.format(blog.name),
            'date_list': blog_years(blog=blog),
            'blog': blog,
            'current_year': current_year,
            }

