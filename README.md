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

