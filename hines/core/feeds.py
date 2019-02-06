from django.contrib.sites.models import Site
from django.templatetags.static import static
from django.contrib.syndication.views import Feed
from django.template import Context, loader, TemplateDoesNotExist
from django.urls import reverse
from django.utils.feedgenerator import Rss201rev2Feed
from django.utils.html import escape

from .recent import RecentObjects
from .utils import get_site_url


class ExtendedRSSFeed(Rss201rev2Feed):
    """
    Create a type of RSS feed generator that has content:encoded elements.

    This is adapted from
    https://github.com/chrisdev/django-wagtail-feeds/blob/master/wagtail_feeds/feeds.py

    To use this for a feed you'll need this and ExtendedFeed (below):

        class MyRSSFeed(ExtendedFeed):

            feed_type = ExtendedRSSFeed

            # EITHER specify a template for the content:encoded HTML:
            content_template = 'app/feeds/content.html'

            # OR a method to return the HTML:
            def item_content(self, item):
                return '<b>This is my HTML for content:encoded.</b>'
    """

    def root_attributes(self):
        attrs = super().root_attributes()
        attrs['xmlns:content'] = 'http://purl.org/rss/1.0/modules/content/'
        return attrs

    def add_root_elements(self, handler):
        super().add_root_elements(handler)

        # Add <image></image> element
        # https://validator.w3.org/feed/docs/rss2.html#ltimagegtSubelementOfLtchannelgt
        image_url = self.channel_image_url()

        if image_url:
            handler.startElement('image', {})
            handler.addQuickElement('url', image_url)
            # Use the same title and link as the feed as a whole:
            handler.addQuickElement('title', self.channel_image_title())
            handler.addQuickElement('link', self.channel_image_link())
            handler.endElement('image')

    def add_item_elements(self, handler, item):
        """
        Use item['content'] to make the content:encoded element.
        """
        super().add_item_elements(handler, item)

        if item['content'] is not None:
            handler.startElement('content:encoded', {})

            content = '<![CDATA['
            content += item['content']
            content += ']]>'

            # Adding content in this way do not escape content so make it
            # suitable for Feedburner and other services. If we use
            # handler.characters(content) then it will escape content and will
            # not work perfectly with Feedburner and other services.
            handler._write(content)

            handler.endElement('content:encoded')

    def channel_image_url(self):
        "URL of the image to use for the feed."
        return '{}{}'.format(get_site_url(), static(
                                            'hines/img/site_icon.jpg'))

    def channel_image_title(self):
        "Might be used for image alt tag."
        return 'Site icon'

    def channel_image_link(self):
        "Might be used to link the image to the site."
        return get_site_url()


class ExtendedFeed(Feed):
    """
    Required to add content:encoded elements to a feed.
    See the comments in ExtendedRSSFeed.
    """
    # Specify the path to a template to use that for the content:encoded data.
    content_template = None

    def item_extra_kwargs(self, item):
        """
        Add 'content' to the item, which will be used to make the
        content:encoded element.
        """
        extra = super().item_extra_kwargs(item)

        extra.update({
            'content': self.get_item_content(item),
        })
        return extra

    def get_item_content(self, item):
        """
        If there's a self.content_template, then render that for the
        content:encoded element, otherwise use the self.item_content() method.
        """
        content_tmp = None

        if self.content_template is not None:
            try:
                content_tmp = loader.get_template(self.content_template)
            except TemplateDoesNotExist:
                pass

        if content_tmp:
            context = {'obj': item,
                       'site_url': get_site_url(),}
            content = content_tmp.render(context)
        else:
            content = self.item_content(item)

        return content

    def item_content(self, item):
        """
        Only used if self.content_template is None.
        """
        return ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['foo'] = 'bar'
        return context


class EverythingFeedRSS(ExtendedFeed):

    num_items = 14

    feed_type = ExtendedRSSFeed

    description_template = 'hines_core/feeds/everything_description.html'

    content_template = 'hines_core/feeds/everything_content.html'

    # Getting details about the feed/site:

    def get_object(self, request):
        return Site.objects.get_current()

    def link(self, obj):
        return get_site_url()

    def title(self, obj):
        return '%s: Everything' % obj.name

    def description(self, obj):
        return 'Things written, created, linked to or liked by Phil Gyford'

    def items(self, obj):
        kinds = (
            ('blog_posts', 'writing'),
            ('blog_posts', 'comments'),
            ('flickr_photos', '35034346050@N01'),
            ('pinboard_bookmarks', 'philgyford'),
        )
        return RecentObjects(kinds).get_objects(num=self.num_items)

    # Getting details for each post in the feed:

    def item_title(self, item):
        if item['kind'] == 'blog_post':
            title = item['object'].title

        elif item['kind'] == 'pinboard_bookmark':
            title = "[Link] {}".format(item['object'].title)

        elif item['kind'] == 'flickr_photos':
            title = 'Photos from {}'.format(item['time'].strftime('%-d %B %Y'))
        else:
            title = item.title

        return title

    def item_link(self, item):
        if item['kind'] == 'flickr_photos':
            t = item['time']
            return reverse('hines:day_archive', kwargs={
                                                    'year': t.year,
                                                    'month': t.strftime('%m'),
                                                    'day': t.strftime('%d') })
        elif item['kind'] == 'blog_post' and item['object'].remote_url:
            # e.g. A comment on another site; link to it there.
            return item['object'].remote_url
        elif item['kind'] == 'pinboard_bookmark':
            # Link to the bookmark's URL itself, not to our permalink.
            return item['object'].url
        else:
            return item['object'].get_absolute_url()

    def item_pubdate(self, item):
        if item['kind'] == 'blog_post':
            return item['object'].time_published

        elif item['kind'] == 'pinboard_bookmark':
            return item['object'].post_time

        elif item['kind'] == 'flickr_photos':
            return item['objects'][0].post_time

    def item_updateddate(self, item):
        if item['kind'] == 'blog_post':
            return item['object'].time_modified

        elif item['kind'] == 'pinboard_bookmark':
            return item['object'].time_modified

        elif item['kind'] == 'flickr_photos':
            dt = None
            for photo in item['objects']:
                if dt is None or photo.last_update_time > dt:
                    dt = photo.last_update_time
            return dt
