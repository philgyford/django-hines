from django.test.client import Client
from django.test import TestCase

import time
from weblog.models import Blog,Entry
from aggregator.models import Aggregator
from django.contrib.comments.forms import CommentSecurityForm
from django.shortcuts import get_object_or_404
from taggit.models import Tag


class WeblogBaseTestCase(TestCase):
    fixtures = ['../../aggregator/fixtures/test_data.json', ]

class ViewsTestCase(WeblogBaseTestCase):

    def test_writing_blog_index(self):
        '''Test if the Writing blog homepage renders.'''
        c = Client()
        response = c.get('/writing/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['blog'].id, 1)
        self.failUnlessEqual(len(response.context['entries'].object_list), 2)
        self.failUnlessEqual(response.context['entries'].object_list[0].slug, 'featured-writing-post')
        self.failUnlessEqual(response.context['entries'].paginator.num_pages, 1)
        self.failUnlessEqual(len(response.context['popular_tags']), 5)
        self.failUnlessEqual(response.context['popular_tags'][2].name, 'cats')
        self.failUnlessEqual(len(response.context['featured_entries']), 1)
        self.failUnlessEqual(response.context['featured_entries'][0].slug, 'featured-writing-post')
    
    def test_links_blog_index(self):
        '''Test if the Links blog homepage renders.'''
        c = Client()
        response = c.get('/links/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['blog'].id, 2)
        self.failUnlessEqual(len(response.context['entries'].object_list), 1)
        self.failUnlessEqual(response.context['entries'].object_list[0].slug, 'links-post-august')

    def test_comments_blog_index(self):
        '''Test if the Comments blog homepage renders.'''
        c = Client()
        response = c.get('/comments/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['blog'].id, 3)
        self.failUnlessEqual(len(response.context['entries'].object_list), 1)
        self.failUnlessEqual(response.context['entries'].object_list[0].title, "The Online Photographer: 'A Leica for a Year' a Year Later")
    
    def test_blog_archive_month(self):
        '''Test if an archive page for a month within a weblog renders.'''
        c = Client()
        response = c.get('/writing/2010/09/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['blog'].id, 1)
        self.failUnlessEqual(len(response.context['entries']), 2)
        self.failUnlessEqual(response.context['date'].year, 2010)
        self.failUnlessEqual(response.context['date'].month, 9)

    def test_blog_archive_year(self):
        '''Test if an archive page for a year within a weblog renders.'''
        c = Client()
        response = c.get('/writing/2010/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['blog'].id, 1)
        self.failUnlessEqual(len(response.context['entries']), 2)
        self.failUnlessEqual(response.context['date'].year, 2010)
        
    def test_entry_detail(self):
        '''Test if a page for a single Entry within a weblog renders.'''
        c = Client()
        response = c.get('/writing/2010/09/27/featured-writing-post/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['blog'].id, 1)
        self.failUnlessEqual(response.context['entry'].slug, 'featured-writing-post')
        self.failUnlessEqual(response.context['entry'].blog.slug, 'writing')
        self.failUnlessEqual(len(response.context['other_blogs']), 3)
        self.failUnlessEqual(len(response.context['other_blogs'][0].entries), 0)

    def test_draft_entry_detail(self):
        '''Test if a page for a single DRAFT Entry within a weblog 404s.'''
        c = Client()
        response = c.get('/writing/2010/09/27/draft-post/')
        self.failUnlessEqual(response.status_code, 404)
        
    def test_blog_tag(self):
        '''Test if a page for a tag within a weblog renders.'''
        c = Client()
        response = c.get('/writing/animals/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['blog'].id, 1)
        self.failUnlessEqual(response.context['tag'].name, 'animals')
        self.failUnlessEqual(len(response.context['entries']), 2)
        self.failUnlessEqual(response.context['entries'][0].slug, 'featured-writing-post')

    def test_blog_tag_404(self):
        '''Test if a page for a non-existent tag within a weblog 404s.'''
        c = Client()
        response = c.get('/writing/fish/')
        self.failUnlessEqual(response.status_code, 404)


class BlogTestCase(WeblogBaseTestCase):
    
    def test_with_entries_manager_method_entry_exclude(self):
        '''Test the correct data is being returned from the with_entries Blog manager method when we use the entry_exclude filter.'''
        
        blogs = Blog.objects.with_entries(
            entry_exclude={
                'pk' : 1
            }
        )
        self.failUnlessEqual(len(blogs), 3)
        for blog in blogs:
            if blog.id == 1:
                self.failUnlessEqual(len(blog.entries), 1)
                self.failUnlessEqual(blog.entries[0].id, 2)
        
    def test_with_entries_manager_method_entry_filter(self):
        '''Test the correct data is being returned from the with_entries Blog manager method when we use the entry_filter filter.'''
        blogs = Blog.objects.with_entries(
            entry_filter={
                'published_date__year' : 2010,
                'published_date__month' : 9,
                'published_date__day' : 26,
            }
        )
        for blog in blogs:
            if blog.id == 1:
                self.failUnlessEqual(len(blog.entries), 1)
                self.failUnlessEqual(blog.entries[0].id, 1)
            elif blog.id == 2:
                self.failUnlessEqual(len(blog.entries), 0)

    def test_with_entries_manager_method_entry_limit(self):
        '''Test the correct data is being returned from the with_entries Blog manager method when we use the entry_limit filter.'''
        blogs = Blog.objects.with_entries(
            entry_limit=1
        )
        for blog in blogs:
            if blog.id == 1:
                self.failUnlessEqual(len(blog.entries), 1)


class EntryTestCase(WeblogBaseTestCase):
    
    def test_draft_entry(self):
        '''Make sure draft entry isn't visible'''
        entries = Entry.live.all()
        hidden = True
        for entry in entries:
            if entry.id == 3:
                hidden = False
        self.failUnlessEqual(hidden, True)
    
    def test_object_manager(self):
        '''Make sure the object manager returns the correct number of Entries.'''
        entries = Entry.objects.all()
        self.failUnlessEqual(len(entries), 5)
        entries = Entry.objects.filter(blog__exact=1)
        self.failUnlessEqual(len(entries), 3)
        
    def test_live_manager(self):
        '''Make sure the live manager is only returning LIVE Entries, and the extra Blog data.'''
        entries = Entry.live.all()
        self.failUnlessEqual(len(entries), 4)
        entries = Entry.live.filter(blog__exact=1)
        self.failUnlessEqual(len(entries), 2)
        self.failUnlessEqual(entries[0].blog.short_name, 'Writing')
    
    def test_htmlize(self):
        '''Make sure the three different kinds of formatting the entry body/body_more work.'''
        entry = Entry()
        entry.body = """Hello *there*.  
        How are you?"""
        
        entry.format = entry.NO_FORMAT
        formatted_body = entry.htmlize_text(entry.body)
        self.assertEquals(formatted_body, u"""Hello *there*.  
        How are you?""")
        
        entry.format = entry.CONVERT_LINE_BREAKS_FORMAT
        formatted_body = entry.htmlize_text(entry.body)
        self.assertEquals(formatted_body, u"""<p>Hello *there*.  <br />        How are you?</p>""")
        
        entry.format = entry.MARKDOWN_FORMAT
        formatted_body = entry.htmlize_text(entry.body)
        self.assertEquals(formatted_body, u"""<p>Hello <em>there</em>.<br />
        How are you?</p>""")
        
    def test_absolute_url_local(self):
        '''Ensure the URL for entries with local URLs is correct.'''
        entry = Entry.live.get(pk=1)
        self.assertEquals(entry.get_absolute_url(), '/writing/2010/09/26/published-writing-post/')

    def test_absolute_url_remote(self):
        '''Ensure the URL for entries with remote URLs is correct.'''
        entry = Entry.live.get(pk=5)
        self.assertEquals(entry.get_absolute_url(), 'http://theonlinephotographer.typepad.com/the_online_photographer/2010/08/a-leica-for-a-year-a-year-later.html')
        
    def test_get_next_published(self):
        '''Make sure get_next_published Entry works.'''
        entry = Entry.live.get(pk=1)
        try:
            next_entry = entry.get_next_published()
            next_id = next_entry.id
        except:
            next_id = 0 # No next entry; shouldn't get here.
        self.assertEquals(next_id, 2)
        
        entry = Entry.live.get(pk=2)
        try:
            next_entry = entry.get_next_published()
            next_id = next_entry.id
        except:
            next_id = 0 # No next entry; should get here.
        self.assertEquals(next_id, 0)
    
    def test_get_previous_published(self):
        '''Make sure get_previous_published Entry works.'''
        entry = Entry.live.get(pk=1)
        try:
            previous_entry = entry.get_previous_published()
            previous_id = previous_entry.id
        except:
            previous_id = 0 # No prev entry; should get here.
        self.assertEquals(previous_id, 0)
        
        entry = Entry.live.get(pk=2)
        try:
            previous_entry = entry.get_previous_published()
            previous_id = previous_entry.id
        except:
            previous_id = 0 # No prev entry; shouldn't get here.
        self.assertEquals(previous_id, 1)

    def test_comments_enabled(self):
        entry = Entry.live.get(pk=1)
        self.failUnlessEqual(entry.comments_enabled(), True)
        
        entry.enable_comments = False
        entry.save()
        self.failUnlessEqual(entry.comments_enabled(), False)
        
        entry.enable_comments = True
        entry.save()
        blog = entry.blog
        blog.enable_comments = False
        blog.save()
        self.failUnlessEqual(entry.comments_enabled(), False)

        blog.enable_comments = True
        blog.save()
        current_aggregator = Aggregator.objects.get_current()
        current_aggregator.enable_comments = False
        current_aggregator.save()
        self.failUnlessEqual(entry.comments_enabled(), False)
        
        current_aggregator.enable_comments = True
        current_aggregator.save()

    def test_blog_feed_local(self):
        '''Test if a blog's local RSS feed renders.'''
        blog = Blog.objects.get(pk=2)
        c = Client()
        response = c.get( blog.get_entries_feed_url() )
        self.failUnlessEqual(response.status_code, 200)

    def test_blog_feed_remote(self):
        '''Test if we we use a remote RSS feed for a blog if one is set.'''
        blog = Blog.objects.get(pk=1)
        self.failUnlessEqual(blog.get_entries_feed_url(), 'http://feeds.feedburner.com/PhilGyfordsWriting')

    def test_tags_on_entry(self):
        '''Test if the correct tags are fetched from an entry.'''
        entry = Entry.live.get(pk=1)
        tags = entry.tags.all()
        self.failUnlessEqual(len(tags), 4)
        self.failUnlessEqual(tags[0].name == 'animals', True)
        self.failUnlessEqual(tags[1].name == 'cake', True)
        self.failUnlessEqual(tags[2].name == 'cats', True)
        self.failUnlessEqual(tags[3].name == 'dogs', True)
    
    def test_entries_with_tag(self):
        '''Make sure we get the correct Entries back for a particular tag.'''
        blog = get_object_or_404(Blog, slug='writing')
        tag = get_object_or_404(Tag, slug='cats')

        entries = list(Entry.live.filter(
                                    blog__slug__exact = blog.slug,
                                    tags__name__in=[tag.slug]
                                ))
        self.failUnlessEqual(len(entries), 1)
        self.failUnlessEqual(entries[0].id, 1)
    
    def test_featured_entries(self):
        featured_entries = Entry.featured_set.all()
        self.failUnlessEqual(len(featured_entries), 1)
        self.failUnlessEqual(featured_entries[0].id, 2)


class CommentTestCase(WeblogBaseTestCase):

    def post_comment(self, entry_id=1):
        """
        Attempts to post a comment to an Entry.
        """
        form = CommentSecurityForm( Entry.live.get(pk=entry_id) )
        timestamp = int(time.time())
        security_hash = form.initial_security_hash(timestamp)
        c = Client()
        response = c.post('/cmnt/post/', { 
                                'name': 'Bobby', 
                                'email': 'bobby@example.com', 
                                'url': '', 
                                'comment': 'Hello.', 
                                'content_type': 'weblog.entry',
                                'timestamp': timestamp,
                                'object_pk': entry_id, 
                                'security_hash': security_hash,
                            },follow=True)
        return response
        
    def test_comment_post(self):
        '''
        Test if posting a comment on an Entry works.
        '''
        response = self.post_comment()
        self.failUnlessEqual(response.status_code, 200)

    def test_comment_post_disabled_entry(self):
        '''
        Test if posting a comment on an Entry that has comments disabled works.
        '''
        entry = Entry.live.get(pk=1)
        entry.enable_comments = False
        entry.save()
        response = self.post_comment()
        entry.enable_comments = True
        entry.save()
        self.failUnlessEqual(response.status_code, 400)

    def test_comment_post_disabled_blog(self):
        '''
        Test if posting a comment on an Entry where the Blog has comments disabled works.
        '''
        entry = Entry.live.get(pk=1)
        blog = entry.blog
        blog.enable_comments = False
        blog.save()
        response = self.post_comment()
        blog.enable_comments = True
        blog.save()
        self.failUnlessEqual(response.status_code, 400)

    def test_comment_post_disabled_aggregator(self):
        '''
        Test if posting a comment on an Entry where the Aggregator has comments disabled works.
        '''
        entry = Entry.live.get(pk=1)
        current_aggregator = Aggregator.objects.get_current()
        current_aggregator.enable_comments = False
        current_aggregator.save()
        response = self.post_comment()
        current_aggregator.enable_comments = True
        current_aggregator.save()
        self.failUnlessEqual(response.status_code, 400)

    def test_entry_comment_count(self):
        '''
        Make sure num_comments on an Entry increments when a comment is posted.
        '''
        entry = Entry.live.get(pk=2)
        self.assertEquals(entry.num_comments, 0)
        self.assertEquals(entry.comments.count(), 0)
        response = self.post_comment(entry_id=2)
        entry = Entry.live.get(pk=2)
        self.assertEquals(entry.num_comments, 1)
        self.assertEquals(entry.comments.count(), 1)
        
