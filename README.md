# django-hines

[![Build Status](https://github.com/philgyford/django-hines/actions/workflows/test.yml/badge.svg)](https://github.com/philgyford/django-hines/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/philgyford/django-hines/branch/main/graph/badge.svg?token=I2JRGN0UPP)](https://codecov.io/gh/philgyford/django-hines)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Code style: prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg?style=flat-square)](https://github.com/prettier/prettier)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

Code for https://www.gyford.com

Pushing to `main` will run the commit through [this GitHub Action](https://github.com/philgyford/django-hines/actions/workflows/main.yml) to run tests, and [Coveralls](https://coveralls.io) to check coverage. If it passes, it will be deployed automatically to the VPS.

When changing the python version, it will need to be changed in:

- `.pre-commit-config.yaml`
- `.python-version`
- `pyproject.toml` (in `project`, `tool.ruff` and `tool.uv.pip`)

For local development we use uv to manage python version and dependencies,
running Django on the local, host machine. Postgres, Redis, and the
asset-building processes are run in a Docker VM.

The live site is on an Ubuntu 22 VPS.

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

    $ docker compose build

Then start up the web, assets and database containers:

    $ docker compose up

There are three containers:

- `hines_db`: the postgres server
- `hines_assets`: the front-end assets builder
- `hines_redis`: the redis server (for django-q2 and optional caching)

### 4. Set up the database

Once that's running, showing the logs, open another terminal window/tab.

There are two ways we can populate the database. First we'll create an empty one, and second we'll populate it with a dump of data from the live site.

#### 4a. An empty database

The `build` step will create the database and run the initial Django migrations.

Then create a superuser:

    $ ./run manage createsuperuser

(See below for more info on the `./run` script.)

#### 4b. Use a dump from the live site

Dump a database on the server with:

    phil$ pg_dump -h localhost -U hines -d hines -Fc -b -f dump.sql

SCP that to this local directory with:

    $ scp username@your.vps.domain.com:/home/username/dump.sql .

Drop the existing dev database:

    $ ./run psql -d postgres
    # drop database hines with (FORCE);
    # create database hines;
    # grant all privileges on database hines to hines;
    # \q

Then copy the dump into Docker and load it into the database:

    $ docker cp dump.sql hines_db:/tmp/
    $ docker exec -i hines_db pg_restore -h localhost -U hines -d hines -j 2 /tmp/dump.sql

### 5. Run the webserver

    $ ./run runserver

And, optionally, as required, the Django-Q process:

    $ ./run djangoq

### 6. Vist and set up the site

Then go to http://www.gyford.test:8000 and you should see the site.

Log in to the [Django Admin](http://www.gyford.test:8000/backstage/), go to the "Sites" section and change the one Site's Domain Name to `www.gyford.test:8000` and the Display Name to "Phil Gyford’s website", if it's not already.

## Ongoing work

### Docker databases

The Postgres and Redis databases, and the assets processing, are in Docker
containers for local development. Start them with:

    $ docker compose up

Stop with:

    $ docker compose down

See details on the `./run` script below for running things inside the containers.

### uv environment

Create a virtual env and install Python dependencies using `uv`:

    $ uv sync

The webserver and optional django-q processes are run on your local machine,
not in Docker:

    $ run runserver

And:

    $ run djangoq

See the `./run` script for more shortcuts.

## Updating dependencies

The live site currently doesn't use `uv`, so we need to keep `requirements.txt`
updated if we change anything:

    $ uv pip compile pyproject.toml -o requirements.txt

### pre-commit

Install [pre-commit](https://pre-commit.com) to run `.pre-commit-config.yml` automatically when `git commit` is done.

### Front-end assets

Gulp is used to build the final CSS and JS file(s), and watches for changes in the `hines_assets` container. Node packages are installed and upgraded using `yarn` (see `./run` below).

## The ./run script

The `./run` script makes it easier to run things that are within the Docker containers. This will list the commands available, which are outlined below:

    $ ./run

### `./run manage`

Run the Django `manage.py` file with any of the usual commands, within the uv virtual environment. e.g.

    $ ./run manage makemigrations

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

Connects to PosgreSQL with psql. Add any required arguments on the end. Uses the `hines` database unless you specify another like:

    $ ./run psql -d databasename

### `./run yarn:outdated`

List any installed Node packages (used for building front end assets) that are outdated.

### `./run yarn:upgrade`

Update any installed Node packages that are outdated.

## VPS set-up

The complete set-up of an Ubuntu VPS is beyond the scope of this README. Requirements:

- Local postgresql
- Local redis (for caching and django-q2)
- pipx, virtualenv and pyenv
- gunicorn
- nginx
- systemd
- cron

### 1. Create a database

    username$ sudo su - postgres
    postgres$ createuser --interactive -P
    postgres$ createdb --owner hines hines
    postgres$ exit

### 2. Create a directory for the code

    username$ sudo mkdir -p /webapps/hines/
    username$ sudo chown username:username /webapps/hines/
    username$ mkdir /webapps/hines/logs/
    username$ cd /webapps/hines/
    username$ git clone git@github.com:philgyford/django-hines.git code

### 3. ## Install python version, set up virtualenv, install python dependencies

    username$ pyenv install --list  # All those available to install
    username$ pyenv versions        # All those already installed and available
    username$ pyenv install 3.10.8  # Whatever version we're using

Make the virtual environment and install pip-tools:

    username$ cd /webapps/hines/code
    username$ virtualenv --prompt hines venv -p $(pyenv which python)
    username$ source venv/bin/activate
    (hines) username$ python -m pip install pip-tools

Install dependencies from `requirements.txt`:

    (hines) username$ pip-sync

### 4. Create `.env` file

    (hines) username$ cp .env.dist .env

Then fill it out as required.

### 5. Set up database

Either do `./manage.py migrate` and `./manage.py createsuperuser` to create a new database, or import an existing database dumbp.

### 6. Set up gunicorn with systemd

Symlink the files in this repo to correct location for systemd:

    username$ sudo ln -s /webapps/hines/code/conf/systemd_gunicorn.socket /etc/systemd/system/gunicorn_hines.socket
    username$ sudo ln -s /webapps/hines/code/conf/systemd_gunicorn.service /etc/systemd/system/gunicorn_hines.service

Start the socket:

    username$ sudo systemctl start gunicorn_hines.socket
    username$ sudo systemctl enable gunicorn_hines.socket

Check the socket status:

    username$ sudo systemctl status gunicorn_hines.socket

Start the service:

    username$ sudo systemctl start gunicorn_hines

### 5. Set up nginx

Symlink the file in this repo to correct location:

    username$ sudo ln -s /webapps/hines/code/conf/nginx.conf /etc/nginx/sites-available/hines

Enable this site:

    username$ sudo ln -s /etc/nginx/sites-available/hines /etc/nginx/sites-enabled/hines

Remove the default site if it's not already:

    username$ sudo rm /etc/nginx/sites-enabled/default

Check configuration before (re)starting nginx:

    username$ sudo nginx -t

Start nginx:

     username$ sudo service nginx start

### 6. Set up django-q2 with systemd

Symlink the file in this repo to the correct location for systemd:

    username$ sudo ln -s /webapps/hines/code/conf/systemd_djangoq.service /etc/systemd/system/djangoq_hines.service

Start the service:

    username$ sudo systemctl start djangoq_hines

#### The tasks we have set up to use with django-q2

**NOTE:** If a task times out, it won't appear in the lists of Successful _or_ Failed tasks.

- Every 10 mins: `hines.core.tasks.publish_scheduled_posts`
- Hourly: `hines.core.tasks.fetch_flickr_photos`, kwargs `days="7", account="35034346050@N01"`
- Hourly: `hines.core.tasks.fetch_lastfm_scrobbles`, kwargs `days="1", account="gyford"`
- Hourly: `hines.core.tasks.fetch_pinboard_bookmarks`, kwargs `recent="20", account="philgyford"`
- Hourly: `hines.core.tasks.fetch_twitter_tweets`, kwargs `recent="200", account="philgyford"`
- Daily: `hines.core.tasks.fetch_lastfm_scrobbles`, kwargs `days="14", account="gyford"`
- Daily: `hines.core.tasks.fetch_twitter_favorites`, kwargs `recent="200", account="philgyford"`
- Daily: `hines.core.tasks.fetch_twitter_files`
- Daily: `hines.core.tasks.update_twitter_tweets`, kwargs `account="philgyford"`
- Daily: `hines.core.tasks.update_twitter_users`, kwargs `account="philgyford"`

Currently times out

- Daily: `hines.core.tasks.fetch_flickr_photosets`, kwargs `account="35034346050@N01"` (took 1m 31s on command line)

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

### Image cache

To clear the cached thumbnail images created by django-imagekit (used by django-spectator):

1. Delete all the images from the `CACHES` directories on S3.
2. Clear the Redis cache, as above.

To re-generate all the cached thumbnail images (which must be done because of the
"Optimistic" cache file strategy):

    (hines) username$ ./manage.py generateimages
