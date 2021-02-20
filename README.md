# django-hines

Code for http://www.gyford.com

[![Build Status](https://github.com/philgyford/django-hines/workflows/CI/badge.svg)](https://github.com/philgyford/django-hines/actions?query=workflow%3ACI) [![Coverage Status](https://coveralls.io/repos/github/philgyford/django-hines/badge.svg?branch=master)](https://coveralls.io/github/philgyford/django-hines?branch=master)

Pushing to `main` will run the commit through [this GitHub Action](https://github.com/philgyford/django-hines/actions?query=workflow%3ACI) to run tests, and [Coveralls](https://coveralls.io) to check coverage. If it passes, it will be deployed automatically to Heroku.


## Local development setup

We use Docker for local development only, not for the live site.


### 1. Create a .env file

Create a `.env` file containing the below (see the Heroku Setup section for
more details about the variables):

    export ALLOWED_HOSTS='*'

    export AWS_ACCESS_KEY_ID='YOUR-ACCESS-KEY'
    export AWS_SECRET_ACCESS_KEY='YOUR-SECRET-ACCESS-KEY'
    export AWS_STORAGE_BUCKET_NAME='your-bucket-name'

    export DJANGO_SECRET_KEY='YOUR-SECRET-KEY'
    export DJANGO_SETTINGS_MODULE='config.settings.development'

    # For use in Django:
    export DATABASE_URL='postgres://hines:hines@hines_db:5432/django-hines'
    # For use in Docker:
    POSTGRES_USER=hines
    POSTGRES_PASSWORD=hines
    POSTGRES_DB=django-hines

    export HCAPTCHA_SITEKEY="YOUR-SITEKEY"
    export HCAPTCHA_SECRET="YOUR-SECRET"

    export HINES_AKISMET_API_KEY="YOUR-KEY"

    export HINES_CLOUDFLARE_ANALYTICS_TOKEN="YOUR-TOKEN"

    export HINES_MAPBOX_API_KEY="YOUR-API-KEY"

    # TBD what this should be when using Docker:
    export REDIS_URL='redis://127.0.0.1:6379/1'


### 2. Set up a local domain name

Open your `/etc/hosts` file in a terminal window by doing:

    $ sudo vim /etc/hosts

Enter your computer's password. Then add this line somewhere in the file and save:

    127.0.0.1 www.gyford.test


### 3. Build the Docker containers

Download, install and run Docker Desktop.

In same directory as this README, build the containers:

    $ docker-compose build

Then start up the web and database containers:

    $ docker-compose up

There are two containers, the webserver (`hines_web`) and the postgres serer (`hines_db`). All the repository's code is mirrored in the web container in the `/code/` directory.


### 4. Set up the database

Once that's running, showing its logs, open another terminal window/tab.

There are two ways we can populate the database. First we'll create an empty one,
and second we'll populate it with a dump of data from the live site.

#### 4a. An empty database

The `build` step will create the database and run the Django migrations.

Then create a superuser:

    $ ./scripts/manage.sh createsuperuser

(NOTE: The `manage.sh` script is a shortcut for a longer command that runs
Django's `manage.py` within the Docker web container.)

#### 4b. Use a dump from the live site

Log into postgres and drop the current (empty) database:

    $ docker exec -it hines_db psql -U hines -d postgres
    # drop database django-hines with (FORCE);
	# create database django-hines;
	# grant all privileges on database "django-hines" to hines;
    # \q

On Heroku, download a backup file of the live site's database and rename it to
something simpler. We'll use "heroku_db_dump" below.

Put the file in the same directory as this README.

Import the data into the database:

    $ docker exec -i hines_db pg_restore --verbose --clean --no-acl --no-owner -U hines -d django-hines < heroku_db_dump


#### 5. Vist and set up the site

Then go to http://www.gyford.test:8000 and you should see the site.

Log in to the [Django Admin](http://www.gyford.test:8000/backstage/), go to the "Sites"
section and change the one Site's Domain Name to `www.gyford.test:8000` and the
Display Name to "Phil Gyford’s Website".


## Ongoing work

Whenever you come back to start work you need to start the containers up again:

    $ docker-compose up

When you want to stop the server, in the terminal window/tab that's showing the logs, hit `Control` and `X` together.

You can check if anything's running by doing this, which will list any Docker processes:

    $ docker ps

Do this in the project's directory to stop containers:

    $ docker-compose stop

You can also open the Docker Desktop app to see a prettier view of what containers you have.

When the containers are running you can open a shell to the web server (exit with `Control` and `D` together):

    $ docker exec -it hines_web sh

You could then run `.manage.py` commands within there:

    $ ./manage.py help

Or, use the shortcut command from *outside* of the Docker container:

    $ ./scripts/manage.sh help

Or you can log into the database:

    $ docker exec -it hines_db psql -U hines -d django-hines

The development environment has [django-extensions](https://django-extensions.readthedocs.io/en/latest/index.html) installed so you can use its `shell_plus` and other commands. e.g.:

    $ ./scripts/manage.sh shell_plus
    $ ./scripts/manage.sh show_urls

To install new python dependencies:

    $ docker exec -it hines_web sh
    # pipenv install module-name


## Running tests

The tests should all pass before committing code, especially to `main`.

Run the tests using this shortcut script:

    $ ./scripts/run-tests.sh

You can run a specific test passing a path in like:

    $ ./scripts/run-tests.sh tests.core.test_views.HomeViewTestCase.test_response_200

After tests run successfully you can open the file `htmlcov/index.html` in a browser to get more detailed information about coverage.


## Editing CSS and JS

We use gulp to process Sass and JavaScript:

    $ gulp watch

To check for any NPM updates:

    $ npm outdated

To update everything to new major versions, first install this globally:

    $ npm install -g npm-check-updates

Then:

    $ ncu -u
    $ npm install


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

`HINES_COMMENTS_ADMIN_FEED_SLUG`: URL slug for the admin-only RSS feed of comments, so it can be at a non-obvious location. Default is `"admin-comments"`.

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

`HINES_CLOUDFLARE_ANALYTICS_TOKEN`: e.g. `'32bc47e0f'` etc. If present, the
Cloudflare Web Analytics tracking code will be put into every page, using this
token. This value is taken from the `HINES_CLOUDFLARE_ANALYTICS_TOKEN`
environment variable. Default is `''`.

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
