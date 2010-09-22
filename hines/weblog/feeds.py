from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.utils.feedgenerator import Rss201rev2Feed
from django.shortcuts import get_object_or_404
from weblog.models import Blog,Entry
from aggregator.models import Aggregator


class ExtendedRSSFeed(Rss201rev2Feed):
    """
    Create a type of RSS feed generator that has content:encoded elements.
    """
    def root_attributes(self):
        attrs = super(ExtendedRSSFeed, self).root_attributes()
        attrs['xmlns:content'] = 'http://purl.org/rss/1.0/modules/content/'
        return attrs
        
    def add_item_elements(self, handler, item):
        super(ExtendedRSSFeed, self).add_item_elements(handler, item)
        handler.addQuickElement(u'content:encoded', item['content_encoded'])
    

class LatestEntriesFeed(Feed):
    """
    The base feed class for displaying a list of Entries.
    Child classes will need to, at a minimum, define an items() method.
    """
    feed_type = ExtendedRSSFeed
    
    # Elements for the top-level, channel.
    
    def title(self, obj):
        return obj.name
    
    def link(self, obj):
        return obj.get_absolute_url()
    
    def description(self, obj):
        return obj.description
    
    
    # Elements for each item.
    
    def item_extra_kwargs(self, item):
        return {'content_encoded': self.item_content_encoded(item)}
    
    def item_title(self, item):
        return item.title
        
    def item_description(self, item):
        return item.excerpt
        
    def item_author_name(self, item):
        if (item.author.get_full_name()):
            return item.author.get_full_name()
        else:
            return item.author
    
    def item_pubdate(self, item):
        return item.published_date
        
    def item_content_encoded(self, item):
        content = item.body_html
        if (item.body_more_html):
            content += item.body_more_html
        return content


class LatestBlogEntriesFeed(LatestEntriesFeed):
    """
    The feed class for showing latest entries from a single blog.
    """
    blog = ''
    
    def get_object(self, request, blog_slug):
        blog = get_object_or_404(Blog, slug=blog_slug)
        self.blog = blog
        return blog

    def items(self):
        return Entry.live.filter(blog__slug__exact = self.blog.slug,)[:5]
        

class LatestAllEntriesFeed(LatestEntriesFeed):
    """
    The feed class for showing latest entries from *all* blogs.
    """
    
    def get_object(self, request):
        current_aggregator = Aggregator.objects.get_current()
        return current_aggregator
        
    def title(self, obj):
        return obj.site.name
    
    def link(self, obj):
        """
        Link to the site's home page.
        """
        return reverse('aggregator_index')
    
    def description(self, obj):
        # Site objects don't have descriptions, but you never know, one day...
        return ''
    
    def items(self):
        return Entry.live.all()[:5]
