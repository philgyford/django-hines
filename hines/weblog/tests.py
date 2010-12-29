from django.test.client import Client
from django.test import TestCase
import datetime, time
from weblog.models import Blog,Entry
from customcomments.models import CommentOnEntry
from aggregator.models import Aggregator
from django.contrib.comments.forms import CommentSecurityForm
from django.shortcuts import get_object_or_404
from taggit.models import Tag
from django.contrib.auth.models import User
from django.conf import settings
from django.core import mail


class WeblogBaseTestCase(TestCase):
    fixtures = [
                '../fixtures/test_data.json',
                '../../aggregator/fixtures/test_data.json',
               ]

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
        self.failUnlessEqual(response.context['popular_tags'][2].name, 'cake')
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
        self.failUnlessEqual(len(response.context['entry_list']), 2)
        self.failUnlessEqual(response.context['month'].year, 2010)
        self.failUnlessEqual(response.context['month'].month, 9)

    def test_blog_archive_year(self):
        '''Test if an archive page for a year within a weblog renders.'''
        c = Client()
        response = c.get('/writing/2010/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['blog'].id, 1)
        self.failUnlessEqual(len(response.context['entry_list']), 2)
        self.failUnlessEqual(response.context['year'], u'2010')
        
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

    def test_blog_feed_local(self):
        '''Test if a blog's local RSS feed renders.'''
        blog = Blog.objects.get(pk=2)
        c = Client()
        response = c.get( blog.get_entries_feed_url() )
        self.failUnlessEqual(response.status_code, 200)
        self.assertContains(response, "<title>A links post from August</title>")
        self.assertContains(response, 'links/2010/08/11/links-post-august/</link>')
        self.assertContains(response, "Even if you don't use the whole...</description>")
        self.assertContains(response, '<content:encoded>&lt;dl class="links"&gt;')

    def test_blog_feed_remote(self):
        '''Test if we we use a remote RSS feed for a blog if one is set.'''
        blog = Blog.objects.get(pk=1)
        self.failUnlessEqual(blog.get_entries_feed_url(), 'http://feeds.feedburner.com/PhilGyfordsWriting')


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

    def test_tags_on_entry(self):
        '''Test if the correct tags are fetched from an entry.'''
        entry = Entry.live.get(pk=1)
        tags = entry.tags.all()
        self.failUnlessEqual(len(tags), 4)
        tag_names = []
        for tag in tags:
            tag_names.append(tag.name)
        self.failUnlessEqual('animals' in tag_names, True)
        self.failUnlessEqual('cake' in tag_names, True)
        self.failUnlessEqual('cats' in tag_names, True)
        self.failUnlessEqual('dogs' in tag_names, True)
        self.failUnlessEqual('fish' in tag_names, False)
    
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

    def test_next_prev_month(self):
        '''Test the monthly next/previous links are correct.'''
        # Add a couple of older entries as well as the two in test_data.
        e1 = Entry(title='Entry in Aug 2010', body='test', blog_id=1, published_date='2010-08-15 10:00:00', author_id=1)
        e1.save()
        e2 = Entry(title='Entry in Dec 2009', body='test', blog_id=1, published_date='2009-12-15 10:00:00', author_id=1)
        e2.save()

        c = Client()
        response = c.get('/writing/2010/09/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['previous_month_correct'], datetime.datetime(year=2010,month=8,day=15,hour=10,minute=0,second=0))
        self.failUnlessEqual(response.context['next_month_correct'], None)
        
        response = c.get('/writing/2010/08/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['previous_month_correct'], datetime.datetime(year=2009,month=12,day=15,hour=10,minute=0,second=0))
        self.failUnlessEqual(response.context['next_month_correct'], datetime.datetime(year=2010,month=9,day=26,hour=15,minute=53,second=45))

        response = c.get('/writing/2009/12/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['previous_month_correct'], None)
        self.failUnlessEqual(response.context['next_month_correct'], datetime.datetime(year=2010,month=8,day=15,hour=10,minute=0,second=0))
        
        e1.delete()
        e2.delete()

    def test_next_prev_year(self):
        '''Test the yearly next/previous links are correct.'''
        # Add a couple of older entries as well as the two in test_data.
        e1 = Entry(title='Entry in Aug 2009', body='test', blog_id=1, published_date='2009-08-15 10:00:00', author_id=1)
        e1.save()
        e2 = Entry(title='Entry in Dec 2007', body='test', blog_id=1, published_date='2007-12-15 10:00:00', author_id=1)
        e2.save()

        c = Client()
        response = c.get('/writing/2010/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['previous_year_correct'], datetime.datetime(year=2009,month=8,day=15,hour=10,minute=0,second=0))
        self.failUnlessEqual(response.context['next_year_correct'], None)

        response = c.get('/writing/2009/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['previous_year_correct'], datetime.datetime(year=2007,month=12,day=15,hour=10,minute=0,second=0))
        self.failUnlessEqual(response.context['next_year_correct'], datetime.datetime(year=2010,month=9,day=26,hour=15,minute=53,second=45))

        response = c.get('/writing/2007/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['previous_year_correct'], None)
        self.failUnlessEqual(response.context['next_year_correct'], datetime.datetime(year=2009,month=8,day=15,hour=10,minute=0,second=0))

        e1.delete()
        e2.delete()
        


class CommentTestCase(WeblogBaseTestCase):

    def post_comment(self, entry_id=1, comment_text='Hello', author_name='Bobby'):
        """
        Attempts to post a comment to an Entry.
        """
        form = CommentSecurityForm( Entry.live.get(pk=entry_id) )
        timestamp = int(time.time())
        security_hash = form.initial_security_hash(timestamp)
        c = Client()
        response = c.post('/cmnt/post/', { 
                                'name': author_name, 
                                'email': 'bobby@example.com', 
                                'url': '', 
                                'comment': comment_text, 
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
        current_aggregator = Aggregator.objects.get_current()
        
        old_setting = current_aggregator.test_comments_for_spam
        current_aggregator.test_comments_for_spam = False 

        entry = Entry.live.get(pk=2)
        self.assertEquals(entry.num_comments, 0)
        self.assertEquals(entry.comments.count(), 0)
        response = self.post_comment(entry_id=2)
        entry = Entry.live.get(pk=2)
        self.assertEquals(entry.num_comments, 1)
        self.assertEquals(entry.comments.count(), 1)

        current_aggregator.test_comments_for_spam = old_setting
    
    def test_comment_form_logged_out(self):
        """
        Make sure the name/email fields appear on the entry_detail page when logged out.
        """
        c = Client()
        response = c.get('/writing/2010/09/26/published-writing-post/')
        self.assertContains(response, 'type="text" name="name"')
        self.assertContains(response, 'type="text" name="email"')

    def test_comment_form_logged_in(self):
        """
        Make sure the name/email fields are hidden and filled-in correctly when logged in.
        """
        u = User.objects.create_user('terry', 'terry@example.com', 'terrypassword')
        u.save()
        c = Client()
        c.login(username='terry', password='terrypassword')
        response = c.get('/writing/2010/09/26/published-writing-post/')
        self.assertContains(response, 'type="hidden" name="name" id="id_name" value="terry"')
        self.assertContains(response, 'type="hidden" name="email" id="id_email" value="terry@example.com"')
        
        u.first_name = 'Terry'
        u.last_name = 'Thomas'
        u.save()
        response = c.get('/writing/2010/09/26/published-writing-post/')
        self.assertContains(response, 'type="hidden" name="name" id="id_name" value="Terry Thomas"')
    
    def test_comment_spam_filter_off(self):
        """
        Ensure that when the spam filter is off, posted comments are public.
        """
        current_aggregator = Aggregator.objects.get_current()
        
        old_setting = current_aggregator.test_comments_for_spam
        current_aggregator.test_comments_for_spam = False

        entry = Entry.live.get(pk=2)
        response = self.post_comment(entry_id=2)
        comment = CommentOnEntry.objects.get(pk=4)
        self.assertEquals(comment.is_public, True)

        current_aggregator.test_comments_for_spam = old_setting

    def test_comment_spam_filter_on(self):
        """
        Ensure that when the spam filter is on, spam comments are not public.
        """
        current_aggregator = Aggregator.objects.get_current()
        
        old_setting = current_aggregator.test_comments_for_spam
        current_aggregator.test_comments_for_spam = True 
        
        old_api_key = current_aggregator.typepad_antispam_api_key
        current_aggregator.typepad_antispam_api_key = settings.TEST_TYPEPAD_ANTISPAM_API_KEY

        entry = Entry.live.get(pk=2)
        # According to the Akismet API, a comment author name of 'viagra-test-123'
        # should always be marked as spam, for testing.
        response = self.post_comment(entry_id=2, author_name='viagra-test-123')
        comment = CommentOnEntry.objects.get(pk=4)
        self.assertEquals(comment.is_public, False)

        current_aggregator.test_comments_for_spam = old_setting
        current_aggregator.typepad_antispam_api_key = old_api_key

    def test_comment_emails_on(self):
        """
        Ensure that an email is sent when a comment is posted and the
        preferences are switched on.
        """
        current_aggregator = Aggregator.objects.get_current()

        old_public = current_aggregator.send_comment_emails_public
        old_nonpublic = current_aggregator.send_comment_emails_nonpublic

        current_aggregator.send_comment_emails_public = True 
        current_aggregator.send_comment_emails_nonpublic = True 

        response = self.post_comment()
        self.assertEqual(len(mail.outbox), 1)

        response = self.post_comment(author_name='viagra-test-123')
        self.assertEqual(len(mail.outbox), 2)

        current_aggregator.send_comment_emails_public = old_public
        current_aggregator.send_comment_emails_nonpublic = old_nonpublic


    def test_comment_emails_off(self):
        """
        Ensure that no emails are sent when comments are posted and the
        preferences are switched off.
        """
        current_aggregator = Aggregator.objects.get_current()

        old_public = current_aggregator.send_comment_emails_public
        old_nonpublic = current_aggregator.send_comment_emails_nonpublic

        current_aggregator.send_comment_emails_public = False 
        current_aggregator.send_comment_emails_nonpublic = False 

        response = self.post_comment()
        self.assertEqual(len(mail.outbox), 0)

        response = self.post_comment(author_name='viagra-test-123')
        self.assertEqual(len(mail.outbox), 0)

        current_aggregator.send_comment_emails_public = old_public
        current_aggregator.send_comment_emails_nonpublic = old_nonpublic



        

    #def test_comment_sanitizing(self):
        #current_aggregator = Aggregator.objects.get_current()
        #old_allowed_comment_tags = current_aggregator.allowed_comment_tags
        #current_aggregator.allowed_comment_tags = 'a:href:title b img:src'

        #response = self.post_comment(comment_text='<b><i>Hello</i>')
        #self.failUnlessEqual(response.status_code, 200)

        #current_aggregator.allowed_comment_tags = old_allowed_comment_tags
