# django-hines

[![Build Status](https://github.com/philgyford/django-hines/workflows/CI/badge.svg)](https://github.com/philgyford/django-hines/actions?query=workflow%3ACI)
[![Coverage Status](https://coveralls.io/repos/github/philgyford/django-hines/badge.svg?branch=main)](https://coveralls.io/github/philgyford/django-hines?branch=main)
[![Code style: prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg?style=flat-square)](https://github.com/prettier/prettier)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Code for https://www.gyford.com

Pushing to `main` will run the commit through [this GitHub Action](https://github.com/philgyford/django-hines/actions/workflows/main.yml) to run tests, and [Coveralls](https://coveralls.io) to check coverage. If it passes, it will be deployed automatically to Heroku.

For local development we use Docker. The live site is on Heroku.

## Local development setup

### 1. Create a .env file

Create a `.env` file containing the below (see the Custom Django Settings section below for more details about the variables):

    export ALLOWED_HOSTS='*'

    export AWS_ACCESS_KEY_ID='YOUR-ACCESS-KEY'
    export AWS_SECRET_ACCESS_KEY='YOUR-SECRET-ACCESS-KEY'
    export AWS_STORAGE_BUCKET_NAME='your-bucket-name'

    export DJANGO_SECRET_KEY='YOUR-SECRET-KEY'
    export DJANGO_SETTINGS_MODULE='config.settings.development'

    # For use in Django:
    export DATABASE_URL='postgres://hines:hines@hines_db:5432/hines'
    # For use in Docker:
    POSTGRES_USER=hines
    POSTGRES_PASSWORD=hines
    POSTGRES_DB=django-hines

    export HCAPTCHA_SITEKEY="YOUR-SITEKEY"
    export HCAPTCHA_SECRET="YOUR-SECRET"

    export HINES_AKISMET_API_KEY="YOUR-API-KEY"

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

Then start up the web, assets and database containers:

    $ docker-compose up

There are three containers, the webserver (`hines_web`), the front-end assets builder (`hines_assets`) and the postgres server (`hines_db`). All the repository's code is mirrored in the web and assets containers in the `/code/` directory.

### 4. Set up the database

Once that's running, showing the logs, open another terminal window/tab.

There are two ways we can populate the database. First we'll create an empty one, and second we'll populate it with a dump of data from the live site.

#### 4a. An empty database

The `build` step will create the database and run the initial Django migrations.

Then create a superuser:

    $ ./run manage createsuperuser

(See below for more info on the `./run` script.)

#### 4b. Use a dump from the live site

Log into postgres and drop the current (empty) database:

    $ ./run psql -d postgres
    # drop database hines with (FORCE);
    # create database hines;
    # grant all privileges on database hines to hines;
    # \q

On Heroku, download a backup file of the live site's database and rename it to something simpler. We'll use "heroku_db_dump" below.

Put the file in the same directory as this README.

Import the data into the database ():

    $ docker exec -i hines_db pg_restore --verbose --clean --no-acl --no-owner -U hines -d hines < heroku_db_dump

#### 5. Vist and set up the site

Then go to http://www.gyford.test:8000 and you should see the site.

Log in to the [Django Admin](http://www.gyford.test:8000/backstage/), go to the "Sites" section and change the one Site's Domain Name to `www.gyford.test:8000` and the Display Name to "Phil Gyford’s website", if it's not already.

## Ongoing work

Whenever you come back to start work you need to start the containers up again by doing this from the project directory:

    $ docker-compose up

When you want to stop the server, then this from the same directory:

    $ docker-compose down

You can check if anything's running by doing this, which will list any Docker processes:

    $ docker ps

See details on the `./run` script below for running things inside the containers.

To have VS Code know what python packages are available you'll need to set up a pipenv environment on your host machine:

    $ pipenv install --dev

This is _only_ used for this purpose. It's apparently possible to use another Docker "remote container" in VS Code but it was way too fiddly for any benefit, compared to this.

### Front-end assets

Gulp is used to build the final CSS and JS file(s), and watches for changes in the `hines_assets` container. Node packages are installed and upgraded using `yarn` (see `./run` below).

## The ./run script

The `./run` script makes it easier to run things that are within the Docker containers. This will list the commands available, which are outlined below:

    ./run

### `./run cmd`

Run any command in the web container. e.g.

    ./run cmd ls -al

### `./run sh`

Starts a Shell session in the web container.

### `./run manage`

Run the Django `manage.py` file with any of the usual commands, within the pipenv virtual environment. e.g.

    ./run manage makemigrations

The development environment has [django-extensions](https://django-extensions.readthedocs.io/en/latest/index.html) installed so you can use its `shell_plus` and other commands. e.g.:

    $ ./run manage shell_plus
    $ ./run manage show_urls

### `./run tests`

It runs `collectstatic` and then runs all the Django tests.

Run a folder, file, or class of tests, or a single test, something like this:

    ./run tests tests.core
    ./run tests tests.core.test_views
    ./run tests tests.core.test_views.HomeViewTestCase
    ./run tests tests.core.test_views.HomeViewTestCase.test_response_200

### `./run coverage`

It runs `collectstatic` and then all the tests with coverage. The HTML report files will be at `htmlcov/index.html`.

### `./run flake8`

Lints the python code with flake8. Add any required arguments on the end.

### `./run black`

Runs the Black formatter over the python code. Add any required arguments on the end.

### `./run psql`

Conects to PosgreSQL with psql. Add any required arguments on the end. Uses the `hines` database unless you specify another like:

    ./run psql -d databasename

### `./run pipenv:outdated`

List any installed python packages (default and develop) that are outdated.

### `./run pipenv:update`

Update any installed python packages (default and develop) that are outdated.

### `./run yarn:outdated`

List any installed Node packages (used for building front end assets) that are outdated.

### `./run yarn:upgrade`

Update any installed Node packages that are outdated.

## Heroku set-up

For hosting on Heroku, we use these add-ons:

- Heroku Postgres
- Heroku Redis (for caching)
- Heroku Scheduler
- Papertrail (for viewing/filtering logs)
- Sentry (for error reporting)

The site will require Config settings to be set-up as in the local development `.env` (above) and see the Django settings (below).

To clear the Redis cache, use our `clear_cache` management command:

    $ heroku run python ./manage.py clear_cache

To clear the cached thumbnail images created by django-imagekit (used by django-spectator):

1. Delete all the images from the `CACHES` directories on S3.
2. Clear the Redis cache, as above.

To re-generate all the cached thumbnail images (which must be done because of the
"Optimistic" cache file strategy):

    $ heroku run python ./manage.py generateimages

Note that by default Heroku's Redis is set up with a `maxmemory-policy` of `noeviction` which will generate OOM (Out Of Memory) errors when the memory limit is reached. This [can be changed](https://devcenter.heroku.com/articles/heroku-redis#maxmemory-policy):

    $ heroku redis:info
    === redis-fishery-12345 (HEROKU_REDIS_NAVY_TLS_URL, ...

Then use that Redis name like:

    $ heroku redis:maxmemory redis-fisher-12345 --policy allkeys-lru

### Heroku Config Vars

Set these Config Vars in Heroku (see the Custom Django Settings section below for more about some of the variables):

```
ALLOWED_HOSTS                       pepysdiary-production.herokuapp.com,www.pepysdiary.com
AWS_ACCESS_KEY_ID                   YOUR-ACCESS-KEY
AWS_SECRET_ACCESS_KEY               YOUR-SECRET-ACCESS-KEY
AWS_STORAGE_BUCKET_NAME             your-bucket-nuame
DJANGO_SECRET_KEY                   YOUR-SECRET-KEY
DJANGO_SETTINGS_MODULE              pepysdiary.settings.production
HCAPTCHA_SECRET                     YOUR-PRIVATE-KEY
HCAPTCHA_SITEKEY                    YOUR-PUBLIC-KEY
HINES_AKISMET_API_KEY               YOUR-API-KEY
HINES_CLOUDFLARE_ANALYTICS_TOKEN    YOUR-TOKEN
HINES_COMMENTS_ADMIN_FEED_SLUG      your-slug
HINES_MAPBOX_API_KEY                YOUR_API_KEY
```

Further settings will be set automatically by add-ons.

## Custom Django Settings

Custom settings that can be in the Django `settings.py` file:

`HINES_AKISMET_API_KEY`: To enable checking submitted comments for spam using [Akismet](https://akismet.com) set this to your API key, a string. If `None` then no spam checking is done using Akismet. `None` is the default. By default this is picked up from a `HINES_AKISMET_API_KEY` environment variable.

`HINES_AUTHOR_NAME`: Name of the site's main author. e.g `'Phil Gyford'`.

`HINES_AUTHOR_EMAIL`: Email of the site's main author. e.g. `'bob@example.com'`.

`HINES_CLOUDFLARE_ANALYTICS_TOKEN`: e.g. `'32bc47e0f'` etc. If present, the
Cloudflare Web Analytics tracking code will be put into every page, using this
token. This value is taken from the `HINES_CLOUDFLARE_ANALYTICS_TOKEN`
environment variable. Default is `''`.

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

`HINES_HOME_PAGE_DISPLAY`: Defines how many of different kinds of thing to
display on the sites's home page. The `'weblog_posts'` uses the `slug` of each
Blog to indicate how many posts of each to display. e.g.:

```python
HINES_HOME_PAGE_DISPLAY = {
    'flickr_photos': 3,
    'pinboard_bookmarks': 3,
    'weblog_posts': {
        'writing': 3,
        'comments': 1,
    },
}
```

Default is an empty dict, `{}`.

`HINES_EVERYTHING_FEED_KINDS`: Which blogs, accounts, etc should be featured
in the 'everything combined' RSS feed? A set of sets, e.g.:

```python
HINES_EVERYTHING_FEED_KINDS = (
    ('blog_posts', 'writing'),
    ('blog_posts', 'comments'),
    ('flickr_photos', '35034346050@N01'),
    ('pinboard_bookmarks', 'philgyford'),
)
```

`HINES_ROOT_DIR`: e.g. `'phil'`. All the pages except things like the very front page and admin will live under this directory. Default is `''` but I haven't tried using it with out a root dir set.

`HINES_SITE_ICON`: Path of an image to represent the site, within the static
directory. e.g. `'hines/img/site_icon.jpg'`.

`HINES_TEMPLATE_SETS`: A set of dicts describing different sets of templates that can be used for PostDetails between certain dates. e.g.:

    HINES_TEMPLATE_SETS = (
    	{'name': 'houston', 'start': '2000-03-01', 'end': '2000-12-31'},
    )

Any Post on the Blog with slug `writing` between those two dates will use the `weblogs/sets/houston/post_detail.html` template and any other Post will use `weblogs/post_detail.html`.

Default is `None`, to disable this behaviour.

`HINES_TIMEFORMAT` strftime to use for displaying times in templates. Default is `'%H:%M'`.

`HINES_USE_HCAPTCHA`: boolean, whether to enable the hCaptcha field on weblog post comment forms.

`HINES_USE_HTTPS`: e.g. `False`. Used when generating full URLs and the request object isn't available. Default `False`.

## Media files

Whether in local dev or Heroku, we need an S3 bucket to store Media files in (Static files are served using Whitenoise).

1. Go to the IAM service, Users, and 'Add User'.

2. Enter a name and check 'Programmatic access'.

3. 'Attach existing policies directly', and select 'AmazonS3FullAccess'.

4. Create user.

5. Save the Access key and Secret key.

6. On the list of Users, click the user you just made and note the User ARN.

7. Go to the S3 service and 'Create Bucket'. Name it, select the region, and click through to create the bucket.

8. Click the bucket just created and then the 'Permissions' tab. Add this policy, replacing `BUCKET-NAME` and `USER-ARN` with yours:

```json
{
  "Statement": [
    {
      "Sid": "PublicReadForGetBucketObjects",
      "Effect": "Allow",
      "Principal": {
        "AWS": "*"
      },
      "Action": ["s3:GetObject"],
      "Resource": ["arn:aws:s3:::BUCKET-NAME/*"]
    },
    {
      "Action": "s3:*",
      "Effect": "Allow",
      "Resource": ["arn:aws:s3:::BUCKET-NAME", "arn:aws:s3:::BUCKET-NAME/*"],
      "Principal": {
        "AWS": ["USER-ARN"]
      }
    }
  ]
}
```

9. Click on 'CORS configuration' and add this:

```xml
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

11. Update the server's environment variables for `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_STORAGE_BUCKET_NAME`.
