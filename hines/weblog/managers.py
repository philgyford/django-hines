from django.db import models


class LiveEntryManager(models.Manager):
    
    def get_query_set(self):
        return super(LiveEntryManager, self).get_query_set().filter(status=self.model.LIVE_STATUS).select_related('blog')


class BlogManager(models.Manager):
    
    def with_entries(self, entry_filter={}, entry_exclude={}, entry_limit=False):
        """
        Returns a list of Blog objects, each one with an entries property containing a list of Entries.
        entry_filter will be used to filter() the Entries from each blog.
        entry_exclude will be used to exclude() the Entries from each blog.
        entry_limit can be the number of Entries to return (default is all).
        """
        from weblog.models import Entry

        blogs = list(self.all())
            
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
