# coding: utf-8
import MySQLdb
import pytz

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from ...models import Blog, Post
from hines.users.models import User

# You'll need to: pip install mysqlclient


# We'll associate all imported Posts with this Django User ID:
USER_ID = 1


class Command(BaseCommand):
    """
    Gets all of a weblog's Entries from the MovableType MySQL database and
    creates a new Django object for each one.

    Usage:
    $ ./manage.py import_mt_entries --mt_blog_id=3 --hines_blog_id=4

    And afterwards, do this:
    $ ./manage.py sqlsequencereset weblogs
    and run the SQL commands it gives you.
    """
    help = "Imports Weblogs Posts from legacy MT MySQL database."

    def add_arguments(self, parser):
        parser.add_argument(
            '--mt_blog_id',
            dest='mt_blog_id',
            required=True,
            type=int,
            help='ID of the Movable Type blog to import',
        )

        parser.add_argument(
            '--hines_blog_id',
            dest='hines_blog_id',
            required=True,
            type=int,
            help='ID of the Hines blog to import into',
        )

    def handle(self, *args, **options):

        try:
            blog = Blog.objects.get(pk=options['hines_blog_id'])
        except Blog.DoesNotExist:
            raise CommandError(
                    "There's no Blog with an id of {}.".format(
                                                    options['hines_blog_id']))

        try:
            author = User.objects.get(pk=USER_ID)
        except User.DoesNotExist:
            raise CommandError(
                    "There's no User with an id of {}.".format(USER_ID))

        db = MySQLdb.connect(host=settings.MT_MYSQL_DB_HOST,
                            user=settings.MT_MYSQL_DB_USER,
                            passwd=settings.MT_MYSQL_DB_PASSWORD,
                            db=settings.MT_MYSQL_DB_NAME,
                            port=int(settings.MT_MYSQL_DB_PORT),
                            charset='utf8',
                            use_unicode=True)

        cur = db.cursor(MySQLdb.cursors.DictCursor)

        # FETCH THE BLOG ENTRIES.

        cur.execute("SELECT entry_id, entry_title, entry_excerpt, entry_text, "
            "entry_text_more, entry_created_on, entry_authored_on, "
            "entry_status, entry_allow_comments, entry_convert_breaks, "
            "entry_basename "
            "FROM mt_entry WHERE entry_blog_id='{}' LIMIT 1".format(
                                                    options['mt_blog_id']))

        for row in cur.fetchall():

            excerpt = '' if row['entry_excerpt'] is None else row['entry_excerpt']

            intro = '' if row['entry_text'] is None else row['entry_text']

            body = '' if row['entry_text_more'] is None else row['entry_text_more']

            if row['entry_status'] == 2:
                status = Post.LIVE_STATUS
            else:
                status = Post.DRAFT_STATUS

            mt_format = row['entry_convert_breaks']
            if  mt_format == '__default__':
                html_format = Post.CONVERT_LINE_BREAKS_FORMAT
            elif mt_format in ['markdown', 'markdown_with_smartypants']:
                html_format = Post.MARKDOWN_FORMAT
            # elif mt_format == 'BooterTransform':
                # Booter Text Transform
            # elif mt_format == 'richtext':
                # RichText
            # elif mt_format == 'textile_2':
                # Textile 2
            else:
                # mt_format == 0
                html_format = Post.NO_FORMAT

            allow_comments = True if row['entry_allow_comments'] == 1 else False

            time_published = row['entry_authored_on'].replace(tzinfo=pytz.utc)

            time_created = row['entry_created_on'].replace(tzinfo=pytz.utc)

            slug = row['entry_basename'].replace('_', '-')

            post_kwargs = {
                'title': row['entry_title'],
                'excerpt': excerpt,
                'intro': intro,
                'body': body,
                'time_published': time_published,
                'slug': slug,
                'html_format': mt_format,
                'status': status,
                'blog': blog,
                'author': author,
                'allow_comments': allow_comments,
            }

            # TODO: Add remote_url.
            # TODO: Trackbacks!
            # TODO: Categories
            # TODO: Tags

            post = Post.objects.create(**post_kwargs)
            post.save()

            post.time_created = time_created
            post.save()

            print('Done: {} -> {}: {}'.format(row['entry_id'],
                                             post.id,
                                             row['entry_title']))

        cur.close()
        db.close()

