# coding: utf-8
import MySQLdb
import pprint
import pytz

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from ...models import Blog, Post
from hines.users.models import User

# You'll need to: pip install mysqlclient


# If True, this won't insert/update into our local database, and will output a
# load of stuff to the command line instead:
DRY_RUN = True


# Which blog are we importing for:
BLOG_SETTINGS = 'writing'
# BLOG_SETTINGS = 'comments'


if BLOG_SETTINGS == 'writing':

    MT_BLOG_ID = 1

    # The ID of the Hines Weblog object to import the Posts into:
    HINES_BLOG_ID = 1

    # We'll associate all imported Posts with this Django User ID:
    USER_ID = 1

    # Fetch any tags for entries in MT and add them to the Hines Posts?
    ADD_TAGS = True

    # If an MT Entry is in a category, add that as a tag to the Hines Post.
    # If False, we ignore categories entirely.
    TURN_CATEGORIES_TO_TAGS = True

    # Do we need to fetch the extra 'remote_url' field for each Post?
    # (This is an 'mt_entry_meta' field in Movable Type that we want to save as
    # an extra field to our Django Post object.)
    ADD_REMOTE_URL = False

elif BLOG_SETTINGS == 'comments':

    MT_BLOG_ID = 27

    HINES_BLOG_ID = 2

    USER_ID = 1

    ADD_TAGS = False

    TURN_CATEGORIES_TO_TAGS = False

    ADD_REMOTE_URL = True


pp = pprint.PrettyPrinter(indent=2)


class Command(BaseCommand):
    """
    Gets all of a weblog's Entries from the MovableType MySQL database and
    creates a new Django object for each one.

    Usage:
    $ ./manage.py import_mt_entries

    And afterwards, do this:
    $ ./manage.py sqlsequencereset weblogs
    and run the SQL commands it gives you.
    """

    help = "Imports Weblogs Posts from legacy MT MySQL database."

    def handle(self, *args, **options):

        if DRY_RUN:
            print("\nTHIS IS A DRY RUN.")
        else:
            print("\nNot a dry run. This is happening.")

        try:
            blog = Blog.objects.get(pk=HINES_BLOG_ID)
        except Blog.DoesNotExist:
            raise CommandError(
                    "There's no Blog with an id of {}.".format(HINES_BLOG_ID))

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

        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        cursor2 = db.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute(
            "SELECT "
                "entry_id, entry_title, entry_excerpt, entry_text, "
                "entry_text_more, entry_created_on, entry_authored_on, "
                "entry_status, entry_allow_comments, entry_convert_breaks, "
                "entry_basename "
            "FROM mt_entry "
            "WHERE entry_blog_id='{}' "
            "AND entry_id=15074 "
            # "ORDER BY entry_id DESC LIMIT 15 "
            "".format(MT_BLOG_ID))

        for entry in cursor.fetchall():

            excerpt = '' if entry['entry_excerpt'] is None else entry['entry_excerpt']

            intro = '' if entry['entry_text'] is None else entry['entry_text']

            body = '' if entry['entry_text_more'] is None else entry['entry_text_more']

            if entry['entry_status'] == 2:
                status = Post.LIVE_STATUS
            else:
                status = Post.DRAFT_STATUS

            mt_format = entry['entry_convert_breaks']
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

            allow_comments = True if entry['entry_allow_comments'] == 1 else False

            time_published = entry['entry_authored_on'].replace(tzinfo=pytz.utc)

            time_created = entry['entry_created_on'].replace(tzinfo=pytz.utc)

            slug = entry['entry_basename'].replace('_', '-')

            post_kwargs = {
                'title': entry['entry_title'],
                'excerpt': excerpt,
                'intro': intro,
                'body': body,
                'time_published': time_published,
                'slug': slug,
                'html_format': html_format,
                'status': status,
                'blog': blog,
                'author': author,
                'allow_comments': allow_comments,
            }

            if ADD_REMOTE_URL:
                # Fetch the remote_url from the mt_entry_meta table.

                cursor2.execute(
                    "SELECT entry_meta_vchar FROM mt_entry_meta "
                    "WHERE entry_meta_entry_id='{}' "
                    "AND entry_meta_type='field.remote_url'".format(
                                                            entry['entry_id']))
                row = cursor2.fetchone()
                if row is not None and row['entry_meta_vchar'] is not None:
                    post_kwargs['remote_url'] = row['entry_meta_vchar']

            # TODO: Trackbacks!

            if DRY_RUN:
                print('\nFetched {}: {}'.format(
                                    entry['entry_id'], entry['entry_title']))
                # pp.pprint(post_kwargs)

            else:
                post = Post.objects.create(**post_kwargs)
                post.save()

                post.time_created = time_created
                post.save()

                print('\nDone: {} -> {}: {}'.format(entry['entry_id'],
                                                  post.id,
                                                  entry['entry_title']))

            tags = []

            if ADD_TAGS:
                cursor2.execute(
                    "SELECT tag_name "
                    "FROM mt_objecttag, mt_tag "
                    "WHERE objecttag_tag_id=tag_id "
                    "AND objecttag_object_datasource='entry' "
                    "AND objecttag_blog_id='{}' "
                    "AND objecttag_object_id='{}'".format(
                                                MT_BLOG_ID, entry['entry_id']))

                for tag in cursor2.fetchall():
                    tags.append(tag['tag_name'])

            if TURN_CATEGORIES_TO_TAGS:
                # If we use any of the categories on the left, we'll also add
                # the tags on the right:
                extra_cats = {
                    'Acting books': ['Acting', 'Books', 'Notes'],
                    'Education': ['Acting',],
                    'Salon Collective': ['Acting',],
                    'City Lit': ['Acting',],
                    'LISPA': ['Acting',],
                    'Method Studio': ['Acting',],
                    'Productions': ['Acting',],
                    'Lilia Litviak': ['Acting', 'Productions',],
                    'Books': ['Notes',],
                    'Periodicals': ['Notes',],
                    'Talks': ['Notes',],
                    'Movable Type': ['Web Development',],
                }

                cursor2.execute(
                    "SELECT category_label "
                    "FROM mt_category, mt_placement "
                    "WHERE placement_category_id=category_id "
                    "AND category_class='category' "
                    "AND placement_blog_id='{}' "
                    "AND placement_entry_id='{}' ".format(
                                            MT_BLOG_ID, entry['entry_id']))

                for cat in cursor2.fetchall():
                    label = cat['category_label']
                    if label not in tags:
                        tags.append(label)

                    if label in extra_cats:
                        for extra_cat in extra_cats[label]:
                            if extra_cat not in tags:
                                tags.append(extra_cat)


            if ADD_TAGS or TURN_CATEGORIES_TO_TAGS:
                if not DRY_RUN:
                    post.tags.add(*tags)

                if len(tags) > 0:
                    print("Tagged: {}".format(', '.join(tags)))


        cursor.close()
        cursor2.close()
        db.close()

