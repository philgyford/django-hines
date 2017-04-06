#! /bin/bash

coverage run --branch --source=. --omit=*/migrations/*.py,manage.py,tests/*.py manage.py test --settings=config.settings.tests
#coverage report
coverage html
