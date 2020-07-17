# django-hines

Code for http://www.gyford.com

[![Build Status](https://travis-ci.org/philgyford/django-hines.svg?branch=master)](https://travis-ci.org/philgyford/django-hines)
[![Coverage Status](https://coveralls.io/repos/github/philgyford/django-hines/badge.svg?branch=master)](https://coveralls.io/github/philgyford/django-hines?branch=master)

Pushing to `master` will run the commit through [Travis](https://travis-ci.org) and [Coveralls](https://coveralls.io). If it passes, and coverage doesn't decrease, it will be deployed automatically to Heroku.

## Local development

### Setup

Install python requirements:

    $ pipenv install --dev

In the Django Admin set the Domain Name of the one Site.

Create a database user with the required privileges:

    $ psql
    # create database django-hines;
    # create user hines with password 'hines';
    # grant all privileges on database "django-hines" to hines;
    # alter user hines createdb;

I got an error ("permission denied for relation django_migrations") later:

    $ psql "django-hines" -c "GRANT ALL ON ALL TABLES IN SCHEMA public to hines;"
    $ psql "django-hines" -c "GRANT ALL ON ALL SEQUENCES IN SCHEMA public to hines;"
    $ psql "django-hines" -c "GRANT ALL ON ALL FUNCTIONS IN SCHEMA public to hines;"

Probably need to do this for a fresh install:

    $ pipenv shell
    $ ./manage.py migrate
    $ ./manage.py collectstatic
    $ ./manage.py createsuperuser

_OR_, download the database backup file from Heroku and do this:

    $ pg_restore -d django-hines my_dump_file

Still in the pipenv shell, generate all the django-spectator thumbnails (which
must be done because of the "Optimistic" cache file strategy):

    $ ./manage.py generateimages

Then run the webserver:

    $ ./manage.py runserver

Then visit http://localhost:8000 or http://127.0.0.1:8000.

### Other local dev tasks

#### Editing CSS and JS

We use gulp to process Sass and JavaScript:

    $ gulp watch

#### Tests

Run tests:

    $ pipenv run ./scripts/run-tests.sh

Run a specific test module, e.g.:

    $ pipenv run ./scripts/run-tests.sh tests.weblogs.models.test_post

Run a specific test e.g.:

    $ pipenv run ./scripts/run-tests.sh tests.weblogs.models.test_post.PostTestCase.test_ordering

To include coverage, do:

    $ pipenv run ./scripts/coverage.sh

and then open `htmlcov/index.html` in a browser.

## Heroku set-up

For hosting on Heroku, we use these add-ons:

- Heroku Postgres
- Heroku Redis (for caching)
- Heroku Scheduler
- Papertrail (for viewing/filtering logs)
- Sentry (for error reporting)

To clear the Redis cache, use our `clear_cache` management command:

    $ heroku run python ./manage.py clear_cache

To clear the cached thumbnail images created by django-imagekit (used by django-spectator):

1. Delete all the images from the `CACHES` directories on S3.
2. Clear the Redis cache, as above.

To generate all the cached thumbnail images (which must be done because of the
"Optimistic" cache file strategy):

    $ heroku run python ./manage.py generateimages

## Django Settings

Custom settings that can be in the django `settings.py` file:

`HINES_AKISMET_API_KEY`: To enable checking submitted comments for spam using [Akismet](https://akismet.com) set this to your API key, a string. If `None` then no spam checking is done using Akismet. `None` is the default. By default this is picked up from a `HINES_AKISMET_API_KEY` environment variable.

`HINES_AUTHOR_NAME`: Name of the site's main author. e.g `'Phil Gyford'`.

`HINES_AUTHOR_EMAIL`: Email of the site's main author. e.g. `'bob@example.com'`.

`HINES_SITE_ICON`: Path of an image to represent the site, within the static
directory. e.g. `'hines/img/site_icon.jpg'`.

`HINES_COMMENTS_ALLOWED`: Whether to allow commenting on blog posts. If
`False`, overrides the settings for individual Blogs and Posts. Default
`True`.

`HINES_COMMENTS_ALLOWED_TAGS`: A list of HTML tags allowed in comments; all others will be stripped. e.g. `['a', 'strong', 'em',]`. Default is: `[a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'strong', 'ul']`.

`HINES_COMMENTS_ALLOWED_ATTRIBUTES`: A dict of attributes allowed in HTML tags in comments; all others will be stripped. e.g. `{'a': ['href', 'title',],}`. Default is: `{'a': ['href', 'title'], 'acronym': ['title'], 'abbr': ['title']}`.

`HINES_COMMENTS_CLOSE_AFTER_DAYS`: An integer indicating whether to close comments on Posts after a certain number of days (assuming they're otherwise allowed). `None` (the default) means ignore this setting. Integers, e.g. `30`, mean "keep comments open until this Post is 30 days old".

`HINES_DATE_FORMAT` strftime to use for displaying dates in templates. Default is `'%-d %b %Y'`.

`HINES_DATE_YEAR_MONTH_FORMAT` strftime to use for displaying a date when it only has a month and a year, in templates. Default is `'%b %Y'`.

`HINES_DATETIME_FORMAT` a string to use when displaying both a date and a time. Default is `'[time] on [date]'` The `[time]` token will be replaced with `HINES_TIME_FORMAT` and the `[date]` token will be replaced with the `HINES_DATE_FORMAT`.

`HINES_FIRST_DATE`: Day Archive pages will 404 for days before this date. e.g.
`2000-03-15`. Default is `False` (dates of any age allowed).

`HINES_GOOGLE_ANALYTICS_ID`: e.g. `'UA-123456-1'`. If present, the Google
Analytics Tracking code will be put into every page, using this ID. This value
is taken from the `HINES_GOOGLE_ANALYTICS_ID` environment variable. Default is `''`.

`HINES_HOME_PAGE_DISPLAY`: Defines how many of different kinds of thing to
display on the sites's home page. The `'weblog_posts'` uses the `slug` of each
Blog to indicate how many posts of each to display. e.g.:

    HINES_HOME_PAGE_DISPLAY = {
    	'flickr_photos': 3,
    	'pinboard_bookmarks': 3,
    	'weblog_posts': {
    		'writing': 3,
    		'comments': 1,
    	},
    }

Default is an empty dict, `{}`.

`HINES_EVERYTHING_FEED_KINDS`: Which blogs, accounts, etc should be featured
in the 'everything combined' RSS feed? A set of sets, e.g.:

    HINES_EVERYTHING_FEED_KINDS = (
        ('blog_posts', 'writing'),
        ('blog_posts', 'comments'),
        ('flickr_photos', '35034346050@N01'),
        ('pinboard_bookmarks', 'philgyford'),
    )

`HINES_ROOT_DIR`: e.g. `'phil'`. All the pages except things like the very
front page and admin will live under this directory. Default is `''` but I
haven't tried using it with out a root dir set.

`HINES_TEMPLATE_SETS`: A set of dicts describing different sets of
templates that can be used for PostDetails between certain dates. e.g.:

    HINES_TEMPLATE_SETS = (
    	{'name': 'houston', 'start': '2000-03-01', 'end': '2000-12-31'},
    )

Any Post on the Blog with slug `writing` between those two dates will use the
`weblogs/sets/houston/post_detail.html` template and any other Post will use
`weblogs/post_detail.html`.

Default is `None`, to disable this behaviour.

`HINES_TIMEFORMAT` strftime to use for displaying times in templates. Default is `'%H:%M'`.

`HINES_USE_HTTPS`: e.g. `False`. Used when generating full URLs and the
request object isn't available. Default `False`.

## Environment variables

We expect some variables to be set in the environment. For local development we
have a `.env` file which is used by pipenv.

These variables are used on both local development and production/Heroku sites:

    ALLOWED_HOSTS
    DJANGO_SECRET_KEY
    DJANGO_SETTINGS_MODULE
    DATABASE_URL
    AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY
    AWS_STORAGE_BUCKET_NAME
    REDIS_URL
    SPECTATOR_GOOGLE_MAPS_API_KEY

For local development, a couple of them should be like this in the `.env` file:

    export DJANGO_SETTINGS_MODULE='config.settings.development'

    export DATABASE_URL='postgres://hines:hines@localhost:5432/django-hines'

`REDIS_URL` is used on prodution and _can be_ used on development, if there's
a redis server running and we set the `CACHES` setting to use it in
`config/settings/development.py`.

## Media files

Whether in local dev or Heroku, we need an S3 bucket to store Media files in
(Static files are served using Whitenoise).

1. Go to the IAM service, Users, and 'Add User'.

2. Enter a name and check 'Programmatic access'.

3. 'Attach existing policies directly', and select 'AmazonS3FullAccess'.

4. Create user.

5. Save the Access key and Secret key.

6. On the list of Users, click the user you just made and note the User ARN.

7. Go to the S3 service and 'Create Bucket'. Name it, select the region, and click through to create the bucket.

8. Click the bucket just created and then the 'Permissions' tab. Add this
   policy, replacing `BUCKET-NAME` and `USER-ARN` with yours:

   ```
   {
   [
   {
   ,
   ,
   {
   "
   ,
   ,
   "
   ]
   ,
   {
   ,
   ,
   [
   ,
   "
   ,
   {
   [
   "
   ]
   }
   }
   ]
   }
   ```

9. Click on 'CORS configuration' and add this:

   ```
   <CORSConfiguration>
   	<CORSRule>
   		<AllowedOrigin>*</AllowedOrigin>
   		<AllowedMethod>GET</AllowedMethod>
   		<MaxAgeSeconds>3000</MaxAgeSeconds>
   		<AllowedHeader>Authorization</AllowedHeader>
   	</CORSRule>
   </CORSConfiguration>
   ```

10. Upload all the files to the bucket in the required location.

11. Update the server's environment variables for `AWS_ACCESS_KEY_ID`,
    `AWS_SECRET_ACCESS_KEY` and `AWS_STORAGE_BUCKET_NAME`.
