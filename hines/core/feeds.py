from django.utils.feedgenerator import Rss201rev2Feed


class ExtendedRSSFeed(Rss201rev2Feed):
    """
    Create a type of RSS feed generator that has content:encoded elements.

    Feeds based on this should have two extra methods, like:

        from django.contrib.syndication.views import Feed

        class MyFeed(Feed):
            feed_type = ExtendedRSSFeed

            def item_extra_kwargs(self, item):
                extra = super().item_extra_kwargs(item)
                extra.update(
                        {'content_encoded': self.item_content_encoded(item)})
                return extra

            def item_content_encoded(self, item):
                # Or however your model generates its complete HTML text:
                return item.full_html
    """
    def root_attributes(self):
        attrs = super().root_attributes()
        attrs['xmlns:content'] = 'http://purl.org/rss/1.0/modules/content/'
        return attrs

    def add_item_elements(self, handler, item):
        super().add_item_elements(handler, item)
        if item['content_encoded'] is not None:
            handler.addQuickElement('content:encoded', item['content_encoded'])

