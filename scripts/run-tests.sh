#!/bin/bash
set -e

# You can optionally pass in a test, or test module or class, as an argument.
# e.g.
# ./run_tests.sh tests.appname.test_models.TestClass.test_a_thing
TESTS_TO_RUN=${1:tests}

docker exec -t hines_web coverage --branch --source=. --omit=*/migrations/*.py,manage.py,tests/*.py run manage.py test --settings=config.settings.tests $TESTS_TO_RUN
flake8
coverage report
coverage html
