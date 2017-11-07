# django-hines

Code for http://www.gyford.com

Very much a work in progress.


## Local development

### Setup

We're using [this Vagrant setup](https://github.com/philgyford/vagrant-heroku-cedar-16-python).

	$ vagrant up

Once done, then, for a fresh install:

	$ vagrant ssh
	vagrant$ cd /vagrant
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

	vagrant$ pg_dump hines =U hines -h localhost -Fc > hines.pgsql

Import:

	vagrant$ pg_restore --verbose --clean --no-acl --no-owner -h localhost -U hines -d hines.pgsql

#### Tests

Run tests:

	vagrant$ ./run-tests.sh

To see coverage you can either open `htmlcov/index.html` in a browser or do:

	vagrant$ coverage report


#### Restarting postgresql

Sometimes it seems to stop.

	vagrant$ /etc/init.d/postgresql start

Password is `vagrant`.


## Django Settings

Custom settings that can be in the django `settings.py` file:

``HINES_ROOT_DIR``: e.g. `'phil'`. All the pages except things like the very
front page and admin will live uner this directory.

``HINES_USE_HTTPS``: e.g. `False`. Used when generating full URLs and the
request object isn't available.

``HINES_ALLOW_COMMENTS``: Whether to allow commenting on blog posts. If
``False``, overrides the settings for individual Blogs and Posts. Default
``True``.

``HINES_COMMENTS_ALLOWED_TAGS``: A list of HTML tags allowed in comments; all others will be stripped. e.g. ``['a', 'strong', 'em',]``. Default is the default list used by Bleach.

``HINES_COMMENTS_ALLOWED_ATTRIBUTES``: A dict of attributes allowed in HTML tags in comments; all others will be stripped. e.g. ``{'a': ['href', 'title',],}``. Default is the default dict used by Bleach.

``HINES_FIRST_DATE``: Day Archive pages will 404 for days before this date. e.g.
``2000-03-15``.

``HINES_TEMPLATE_SETS``: A set of dicts describing different sets of
templates that can be used for PostDetails between certain dates. e.g.:
	
	HINES_TEMPLATE_SETS = (
		{'name': 'houston', 'start': '2000-03-01', 'end': '2000-12-31'},
    )	

Any Post on the Blog with slug `writing` between those two dates will use the
`weblogs/sets/houston/post_detail.html` template and any other Post will use
`weblogs/post_detail.html`.
	
