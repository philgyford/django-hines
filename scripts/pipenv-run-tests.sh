#!/bin/sh
set -e

# This script is called by using the shortcut defined in Pipfile:
# pipenv run tests

# You can optionally pass in a test, or test module or class, as an argument.
# e.g.
# ./pipenv-run-tests.sh tests.appname.test_models.TestClass.test_a_thing
TESTS_TO_RUN=${1:tests}

coverage run --branch --source=. --omit=*/migrations/*.py,manage.py,tests/*.py manage.py test --settings=config.settings.tests $TESTS_TO_RUN
flake8
coverage html