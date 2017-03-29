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

