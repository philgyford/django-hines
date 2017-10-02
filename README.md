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

Run tests:

	vagrant$ ./run-tests.sh

To see coverage you can either open `htmlcov/index.html` in a browser or do:

	vagrant$ coverage report


## Django Settings

Custom settings that can be in the django `settings.py` file:

``HINES_ALLOW_COMMENTS``: Whether to allow commenting on blog posts. If
``False``, overrides the settings for individual Blogs and Posts. Default
``True``.

``HINES_COMMENTS_ALLOWED_TAGS``: A list of HTML tags allowed in comments; all others will be stripped. e.g. ``['a', 'strong', 'em',]``. Default is the default list used by Bleach.

``HINES_COMMENTS_ALLOWED_ATTRIBUTES``: A dict of attributes allowed in HTML tags in comments; all others will be stripped. e.g. ``{'a': ['href', 'title',],}``. Default is the default dict used by Bleach.

