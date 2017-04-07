# django-hines

Code for http://www.gyford.com

Very much a work in progress.

## Local development

	$ pip install -r requirements/local.txt

We might have a `.env` file with environment variables in, like:

	export DJANGO_SETTINGS_MODULE=config.settings.local

So:

	$ source .env

Then:

	$ ./manage.py runserver

Run tests:

	$ ./run-tests.sh

To see coverage you can either open `htmlcov/index.html` in a browser or do:

	$ coverage report

To check Whitenoise is compressing and loading static assets correctly while using the Django development server:

	* Run `./manage.py collectstatic`.
	* Set `DEBUG = False` in `config/settings/local.py`.


## Django Settings

Custom settings that can be in the django `settings.py` file:

``HINES_ALLOW_COMMENTS``: Whether to allow commenting on blog posts. If
``False``, overrides the settings for individual Blogs and Posts. Default
``True``.

``HINES_COMMENTS_ALLOWED_TAGS``: A list of HTML tags allowed in comments; all others will be stripped. e.g. ``['a', 'strong', 'em',]``. Default is the default list used by Bleach.

``HINES_COMMENTS_ALLOWED_ATTRIBUTES``: A dict of attributes allowed in HTML tags in comments; all others will be stripped. e.g. ``{'a': ['href', 'title',],}``. Default is the default dict used by Bleach.

