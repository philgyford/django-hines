from django import template


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
