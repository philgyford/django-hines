import contextlib
import re
from xml.sax.saxutils import XMLGenerator

from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib.syndication.views import Feed
from django.template import TemplateDoesNotExist, loader
from django.templatetags.static import static
from django.utils.feedgenerator import Rss201rev2Feed
from django.utils.xmlutils import SimplerXMLGenerator, UnserializableContentError

from hines.core import app_settings
from hines.core.utils import get_site_url


class HinesSimplerXMLGenerator(SimplerXMLGenerator):
    """
    A tweaked XML Generator that won't escape strings that begin with
    '<![CDATA['
    From https://stackoverflow.com/a/68530135/250962
    """

    def addQuickElement(self, name, contents=None, attrs=None):  # noqa: N802
        "Convenience method for adding an element with no children"
        if attrs is None:
            attrs = {}
        self.startElement(name, attrs)
        if contents is not None:
            if contents.startswith("<![CDATA["):
                self.unescaped_characters(contents)
            else:
                self.characters(contents)
        self.endElement(name)

    def unescaped_characters(self, content):
        if content and re.search(r"[\x00-\x08\x0B-\x0C\x0E-\x1F]", content):
            # Fail loudly when content has control chars (unsupported in XML 1.0)
            # See https://www.w3.org/International/questions/qa-controls
            msg = "Control characters are not supported in XML 1.0"
            raise UnserializableContentError(msg)
        XMLGenerator.ignorableWhitespace(self, content)


class ExtendedRSSFeed(Rss201rev2Feed):
    """
    Create a type of RSS feed generator that has <content:encoded>
    elements and <image> elements.

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

    content_type = "application/xml; charset=utf-8"

    def write(self, outfile, encoding):
        "Override default write() method just to use our new XML Generator"
        handler = HinesSimplerXMLGenerator(outfile, encoding)
        handler.startDocument()
        handler.startElement("rss", self.rss_attributes())
        handler.startElement("channel", self.root_attributes())
        self.add_root_elements(handler)
        self.write_items(handler)
        self.endChannelElement(handler)
        handler.endElement("rss")

    def rss_attributes(self):
        attrs = super().rss_attributes()
        attrs["xmlns:content"] = "http://purl.org/rss/1.0/modules/content/"
        return attrs

    def add_root_elements(self, handler):
        super().add_root_elements(handler)

        # Add <image></image> element
        # https://validator.w3.org/feed/docs/rss2.html#ltimagegtSubelementOfLtchannelgt
        image_url = self.channel_image_url()

        if image_url:
            handler.startElement("image", {})
            handler.addQuickElement("url", image_url)
            # Use the same title and link as the feed as a whole:
            handler.addQuickElement("title", self.channel_image_title())
            handler.addQuickElement("link", self.channel_image_link())
            handler.endElement("image")

    def add_item_elements(self, handler, item):
        "Use item['content'] to make the content:encoded element."
        super().add_item_elements(handler, item)

        if item["content"] is not None:
            content = "<![CDATA[" + item["content"] + "]]>"
            handler.addQuickElement("content:encoded", content, {})

    def channel_image_url(self):
        "URL of the image to use for the feed."
        url = static(app_settings.SITE_ICON)
        return f"{get_site_url()}{url}"

    def channel_image_title(self):
        "Might be used for image alt tag."
        return "Site icon"

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

    def __call__(self, request, *args, **kwargs):
        response = super().__call__(request, *args, **kwargs)

        xsl_url = staticfiles_storage.url("hines/xsl/pretty-feed-v3a.xsl").encode(
            "utf-8"
        )

        tag = b'<?xml-stylesheet type="text/xsl" href="' + xsl_url + b'"?>\n'
        start = b"<rss version"

        response.content = response.content.replace(start, tag + start)

        return response

    def item_extra_kwargs(self, item):
        """
        Add 'content' to the item, which will be used to make the
        content:encoded element.
        """
        extra = super().item_extra_kwargs(item)

        extra.update({"content": self.get_item_content(item)})
        return extra

    def get_item_content(self, item):
        """
        If there's a self.content_template, then render that for the
        content:encoded element, otherwise use the self.item_content() method.
        """
        content_tmp = self._get_content_template()

        if content_tmp:
            context = {"obj": item, "site_url": get_site_url()}
            content = content_tmp.render(context)
        else:
            content = self.item_content(item)

        return content

    def item_content(self, item):
        """
        Only used if self.content_template is None.
        """
        return ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["foo"] = "bar"
        return context

    def _get_content_template(self):
        content_tmp = None

        if self.content_template is not None:
            with contextlib.suppress(TemplateDoesNotExist):
                content_tmp = loader.get_template(self.content_template)
        return content_tmp
