#!/usr/bin/env bash

# Much of this copied from Nick Janetakis
# https://github.com/nickjj/docker-django-example/blob/main/run

set -eo pipefail

DC="${DC:-exec}"

# If we're running in CI we need to disable TTY allocation for docker-compose
# commands that enable it by default, such as exec and run.
TTY=""
if [[ ! -t 1 ]]; then
  TTY="-T"
fi


# -----------------------------------------------------------------------------
# Helper functions start with _ and aren't listed in this script's help menu.
# -----------------------------------------------------------------------------

function _dc {
  docker-compose "${DC}" ${TTY} "${@}"
}

function _build_run_down {
  docker-compose build
  docker-compose run ${TTY} "${@}"
  docker-compose down
}


# -----------------------------------------------------------------------------

function cmd {
  # Run any command you want in the web container
  _dc web "${@}"
}


function sh {
  # Start a Shell session in the web container
  cmd sh "${@}"
}


function manage {
  # Run any manage.py commands
  cmd pipenv run python manage.py "${@}"
}


function tests {
  # Run the Django tests
  manage collectstatic --settings=config.settings.tests --no-input
  manage test --settings=config.settings.tests "${@}"
}


function coverage {
  # Run the tests and generate a coverage report in htmlcov/
  manage collectstatic --settings=config.settings.tests --no-input
  cmd pipenv run coverage run manage.py test --settings=config.settings.tests tests
  cmd pipenv run coverage html
}


function flake8 {
  # Lint Python code with flake8
  cmd pipenv run flake8 "${@}"
}


function black {
  # Format Python code with black
  cmd pipenv run black . "${@}"
}


function psql {
  # Connect to PostgreSQL with psql
  # shellcheck disable=SC1091
  . .env
 _dc db psql -U "${POSTGRES_USER}" "${@}"
}


# function redis-cli {
#   # Connect to Redis with redis-cli
#   _dc redis redis-cli "${@}"
# }


function pipenv:outdated {
  # List any installed packages that are outdated
  cmd pipenv update --outdated --dev
}


function pipenv:update {
  # Update any outdated packages
  cmd pipenv update --dev
}


# function pipenv:install {
#   # Install pip3 dependencies and write lock file
#   # (untested)
#   _build_run_down web sh -c "pipenv install"
# }


function yarn:outdated {
  # List any installed yarn packages that are outdated
  _dc yarn outdated
}


function yarn:upgrade {
  # Upgrade yarn dependencies.
  _dc yarn upgrade
}


# function yarn:install {
#   # Install yarn dependencies and write lock file
#   # (untested)
#   _build_run_down webpack yarn install
# }


function help {
  printf "%s <task> [args]\n\nTasks:\n" "${0}"

  compgen -A function | grep -v "^_" | cat -n

  printf "\nExtended help:\n  Each task has comments for general usage\n"
}

# This idea is heavily inspired by: https://github.com/adriancooney/Taskfile
TIMEFORMAT=$'\nTask completed in %3lR'
time "${@:-help}"