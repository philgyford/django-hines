# django-hines

[![Build Status](https://github.com/philgyford/django-hines/workflows/CI/badge.svg)](https://github.com/philgyford/django-hines/actions?query=workflow%3ACI)
[![codecov](https://codecov.io/gh/philgyford/django-hines/branch/main/graph/badge.svg?token=I2JRGN0UPP)](https://codecov.io/gh/philgyford/django-hines)
[![Code style: prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg?style=flat-square)](https://github.com/prettier/prettier)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

Code for https://www.gyford.com

Pushing to `main` will run the commit through [this GitHub Action](https://github.com/philgyford/django-hines/actions/workflows/main.yml) to run tests, and [Coveralls](https://coveralls.io) to check coverage. If it passes, it will be deployed automatically to Heroku.

For local development we use Docker. The live site is on Heroku.

## Local development setup

### 1. Create a .env file

Copy `.env.dist` to `.env` and alter any necessary settings.

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

### Docker

Whenever you come back to start work you need to start the containers up again by doing this from the project directory:

    $ docker-compose up

When you want to stop the server, then this from the same directory:

    $ docker-compose down

You can check if anything's running by doing this, which will list any Docker processes:

    $ docker ps

See details on the `./run` script below for running things inside the containers.

### Python dependencies with virtualenv and pip-tools

Adding and removing python depenencies is most easily done with a virtual environment on your host machine. This also means you can use that environment easily in VS Code.

Set up and activate a virtual environment on your host machine using [virtualenv](https://virtualenv.pypa.io/en/latest/):

    $ virtualenv --prompt . venv
    $ source venv/bin/activate

We use [pip-tools](https://pip-tools.readthedocs.io/en/latest/) to generate `requirements.txt` from `requirements.in`, and install the dependencies. Install the current dependencies into the activated virtual environment:

    (venv) $ python -m pip install -r requirements.txt

To add a new depenency, add it to `requirements.in` and then regenerate `requirements.txt`:

    (venv) $ pip-compile --upgrade --quiet --generate-hashes

And do the `pip install` step again to install.

To remove a dependency, delete it from `requirements.in`, run that same `pip-compile` command, and then:

    (venv) $ python -m pip uninstall <module-name>

To update the python dependencies in the Docker container, this should work:

    $ ./run pipsync

But you might have to do `docker-compose build` instead?

### pre-commit

Install [pre-commit](https://pre-commit.com) to run `.pre-commit-config.yml` automatically when `git commit` is done.

### Front-end assets

Gulp is used to build the final CSS and JS file(s), and watches for changes in the `hines_assets` container. Node packages are installed and upgraded using `yarn` (see `./run` below).

## The ./run script

The `./run` script makes it easier to run things that are within the Docker containers. This will list the commands available, which are outlined below:

    $ ./run

### `./run cmd`

Run any command in the web container. e.g.

    $ ./run cmd ls -al

### `./run sh`

Starts a Shell session in the web container.

### `./run manage`

Run the Django `manage.py` file with any of the usual commands, within the pipenv virtual environment. e.g.

    $ ./run manage makemigrations

The development environment has [django-extensions](https://django-extensions.readthedocs.io/en/latest/index.html) installed so you can use its `shell_plus` and other commands. e.g.:

    $ ./run manage shell_plus
    $ ./run manage show_urls

### `./run tests`

Runs all the Django tests. If it complains you might need to do `./run manage collecstatic` first.

Run a folder, file, or class of tests, or a single test, something like this:

    $ ./run tests tests.core
    $ ./run tests tests.core.test_views
    $ ./run tests tests.core.test_views.HomeViewTestCase
    $ ./run tests tests.core.test_views.HomeViewTestCase.test_response_200

### `./run coverage`

Run all the tests with coverage. The HTML report files will be at `htmlcov/index.html`.

### `./run psql`

Conects to PosgreSQL with psql. Add any required arguments on the end. Uses the `hines` database unless you specify another like:

    $ ./run psql -d databasename

### `./run pipsync`

Update the installed python depenencies depending on the contents of `requirements.txt`.

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

### Heroku Config settings

The site will require Config settings to be set-up, the same as the variables defined in `.env.dist`. In addition, this must be set or Heroku complains:

    DJANGO_SETTINGS_MODULE      hines.config.settings

#EE Website cache

Assuming `HINES_CACHE` is `redis`, and `HINES_USE_REDIS_CACHE` is `True`, and one or
other of the Redis URLs are set...

To clear the Redis cache, use our `clear_cache` management command:

    $ heroku run python ./manage.py clear_cache

Note that by default Heroku's Redis is set up with a `maxmemory-policy` of `noeviction` which will generate OOM (Out Of Memory) errors when the memory limit is reached. This [can be changed](https://devcenter.heroku.com/articles/heroku-redis#maxmemory-policy):

    $ heroku redis:info
    === redis-fishery-12345 (HEROKU_REDIS_NAVY_TLS_URL, ...

Then use that Redis name like:

    $ heroku redis:maxmemory redis-fisher-12345 --policy allkeys-lru

### Image cache

To clear the cached thumbnail images created by django-imagekit (used by django-spectator):

1. Delete all the images from the `CACHES` directories on S3.
2. Clear the Redis cache, as above.

To re-generate all the cached thumbnail images (which must be done because of the
"Optimistic" cache file strategy):

    $ heroku run python ./manage.py generateimages

### Schedule tasks

Here are the tasks that, at time of writing, are set to run using Heroku Scheduler:

- Every 10 mins: `./manage.py publish_scheduled_posts`
- Every 10 mins: `./manage.py fetch_lastfm_scrobbles --account=gyford --days=1`
- Every 10 mins: `./manage.py pending_mentions`
- Hourly: `./manage.py fetch_flickr_photos --account=35034346050@N01 --days=30`
- Hourly: `./manage.py fetch_pinboard_bookmarks --account=philgyford --recent=20`
- Hourly: `./manage.py fetch_twitter_tweets --account=philgyford --recent=200`
- Daily: `./manage.py fetch_flickr_photosets --account=35034346050@N01`
- Daily: `./manage.py fetch_lastfm_scrobbles --account=gyford --days=14`
- Daily: `./manage.py update_twitter_tweets --account=philgyford`
- Daily: `./manage.py update_twitter_users --account=philgyford`
- Daily: `./manage.py fetch_twitter_favorites --account=philgyford --recent=200`
- Daily: `./manage.py fetch_twitter_files`

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
