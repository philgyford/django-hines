# django-hines

Code for http://www.gyford.com

Very much a work in progress.

[![Build Status](https://travis-ci.org/philgyford/django-hines.svg?branch=master)](https://travis-ci.org/philgyford/django-hines)
[![Coverage Status](https://coveralls.io/repos/github/philgyford/django-hines/badge.svg?branch=master)](https://coveralls.io/github/philgyford/django-hines?branch=master)


## Local development

### Setup

We're using [this Vagrant setup](https://github.com/philgyford/vagrant-heroku-cedar-16-python). Media files are stored in an S3 bucket.

	$ vagrant up

Once done, then, for a fresh install:

	$ vagrant ssh
	vagrant$ cd /vagrant
	vagrant$ source .env
	vagrant$ ./manage.py migrate
	vagrant$ ./manage.py collectstatic
	vagrant$ ./manage.py createsuperuser
	vagrant$ ./manage.py runserver 0.0.0.0:5000

Then visit http://localhost:5000 or http://127.0.0.1:5000.

In the Django Admin set the Domain Name of the one Site.

### Other local dev tasks

#### Importing old MT weblog

Make sure Blogs 1 (Writing) and 2 (Comments) have been added in admin.

Install requirements (might only need the last):

	vagrant$ sudo apt-get install libmysqlclient-dev
	vagrant$ pip install mysqlclient

In one window:

	vagrant$ ssh -L 3307:127.0.0.1:3306 MYUSERNAME@MYHOSTNAME

Then in another:

	vagrant$ ./vagrant/manage.py import_mt_entries

#### Importing old Reading

Install `libmysqlclient-dev` as above. Then (yes I used a different python
module for MySQL, grr):

	vagrant$ pip install pymysql

Open SSH connection in one window as above.

Then in another:

	vagrant$ ./vagrant/manage.py import_gyford_reading

#### Postgresql export/import

Export:

	vagrant$ pg_dump hines -U hines -h localhost -Fc > hines.pgsql

Import:

	vagrant$ pg_restore --verbose --clean --no-acl --no-owner -h localhost -U hines -d hines.pgsql


#### Tests

Run tests:

	vagrant$ ./scripts/run-tests.sh

To include coverage, do:

	vagrant$ ./scripts/coverage.sh

and then open `htmlcov/index.html` in a browser.


#### Restarting postgresql

Sometimes it seems to stop.

	vagrant$ /etc/init.d/postgresql start

Password is `vagrant`.


## Django Settings

Custom settings that can be in the django `settings.py` file:

``HINES_ALLOW_COMMENTS``: Whether to allow commenting on blog posts. If
``False``, overrides the settings for individual Blogs and Posts. Default
``True``.

``HINES_COMMENTS_ALLOWED_TAGS``: A list of HTML tags allowed in comments; all others will be stripped. e.g. ``['a', 'strong', 'em',]``. Default is the default list used by Bleach.

``HINES_COMMENTS_ALLOWED_ATTRIBUTES``: A dict of attributes allowed in HTML tags in comments; all others will be stripped. e.g. ``{'a': ['href', 'title',],}``. Default is the default dict used by Bleach.

``HINES_FIRST_DATE``: Day Archive pages will 404 for days before this date. e.g.
``2000-03-15``.

``HINES_GOOGLE_ANALYTICS_ID``: e.g. ``'UA-123456-1'``. If present, the Google
Analytics Tracking code will be put into every page, using this ID. This value
is taken from the ``HINES_GOOGLE_ANALYTICS_ID`` environment variable.

``HINES_ROOT_DIR``: e.g. `'phil'`. All the pages except things like the very
front page and admin will live uner this directory.

``HINES_TEMPLATE_SETS``: A set of dicts describing different sets of
templates that can be used for PostDetails between certain dates. e.g.:
	
	HINES_TEMPLATE_SETS = (
		{'name': 'houston', 'start': '2000-03-01', 'end': '2000-12-31'},
    )

Any Post on the Blog with slug `writing` between those two dates will use the
`weblogs/sets/houston/post_detail.html` template and any other Post will use
`weblogs/post_detail.html`.

``HINES_USE_HTTPS``: e.g. `False`. Used when generating full URLs and the
request object isn't available.


``HINES_HOME_PAGE_DISPLAY``: Defines how many of different kinds of thing to
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

## Environment variables

We expect some variables to be set in the environment. In Vagrant we have
a `.env` file which can be `source`d to do this.

These variables are used on both local/Vagrant and production/Heroku sites:

    ALLOWED_HOSTS
	DJANGO_SECRET_KEY
	DJANGO_SETTINGS_MODULE
	DATABASE_URL
	AWS_ACCESS_KEY_ID
	AWS_SECRET_ACCESS_KEY
	AWS_STORAGE_BUCKET_NAME

	
## Media files

Whether using Vagrant or Heroku, we need an S3 bucket to store Media files in
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
		"Statement": [
			{
			  "Sid":"PublicReadForGetBucketObjects",
			  "Effect":"Allow",
			  "Principal": {
					"AWS": "*"
				 },
			  "Action":["s3:GetObject"],
			  "Resource":["arn:aws:s3:::BUCKET-NAME/*"
			  ]
			},
			{
				"Action": "s3:*",
				"Effect": "Allow",
				"Resource": [
					"arn:aws:s3:::BUCKET-NAME",
					"arn:aws:s3:::BUCKET-NAME/*"
				],
				"Principal": {
					"AWS": [
						"USER-ARN"
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

