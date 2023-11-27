from django import template

from hines.blocks.models import Block

register = template.Library()


@register.inclusion_tag("blocks/block.html")
def render_block(slug):
    """
    Displays the Block as specified by its `slug`.
    """
    try:
        block = Block.objects.get(slug=slug)
    except Block.DoesNotExist:
        return {}
    else:
        return {
            "block": block,
        }
