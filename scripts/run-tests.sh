#!/bin/bash
set -e

# Call this from the host machine to run tests in Docker.

# You can optionally pass in a test, or test module or class, as an argument.
# e.g.
# ./run-tests.sh tests.appname.test_models.TestClass.test_a_thing
TESTS_TO_RUN=${1:-tests}

# Coverage config is in setup.cfg
docker exec hines_web /bin/sh -c "pipenv run coverage run manage.py test --settings=config.settings.tests $TESTS_TO_RUN ; pipenv run flake8 ; pipenv run coverage html"