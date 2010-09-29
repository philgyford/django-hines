from django.db import models
from django.contrib.sites.models import Site


class LiveEntryManager(models.Manager):
    
    def get_query_set(self):
        return super(LiveEntryManager, self).get_query_set().filter(
            status=self.model.LIVE_STATUS,
            site=Site.objects.get_current(),
        ).select_related('blog')


class FeaturedEntryManager(models.Manager):
    
    def get_query_set(self):
        return super(FeaturedEntryManager, self).get_query_set().filter(
            status=self.model.LIVE_STATUS,
            site=Site.objects.get_current(),
            featured=True,
        ).select_related('blog')


class BlogManager(models.Manager):
    
    def with_entries(self, entry_filter={}, entry_exclude={}, entry_limit=False):
        """
        Returns a list of Blog objects, each one with an entries property containing a list of Entries.
        entry_filter will be used to filter() the Entries from each blog.
        entry_exclude will be used to exclude() the Entries from each blog.
        entry_limit can be the number of Entries to return (default is all).
        """
        from weblog.models import Entry

        blogs = super(BlogManager, self).get_query_set().filter(
            site=Site.objects.get_current()
        )
        
        for blog in blogs:
            entry_filter['status'] = Entry.LIVE_STATUS
            
            # This could be less clunkily arranged:
            if entry_limit:
                blog.entries = list( 
                    blog.entry_set
                        .filter(**entry_filter)
                        .exclude(**entry_exclude)
                        .select_related('blog')[:entry_limit]
                )
            else:
                blog.entries = list(
                    blog.entry_set
                        .filter(**entry_filter)
                        .exclude(**entry_exclude)
                        .select_related('blog')
                 )
            
            # Instead of having select_related('blog') on there, we could do this:
            # for blog_entry in blog.entries:
            #     blog_entry.blog = blog
            # Which seems wronger, although it seems to work and is easier on the database.
        
        return blogs
