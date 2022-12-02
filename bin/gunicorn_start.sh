#!/bin/bash

# Do this for the --name argument to work:
# pip install setproctitle

NAME="hines_app"                                  # Name of the application
DJANGODIR=/webapps/hines/code                     # Django project directory
SOCKFILE=/webapps/hines/run/gunicorn.sock         # we will communicte using this unix socket
USER=phil                                         # the user to run as
GROUP=phil                                        # the group to run as
NUM_WORKERS=3                                     # (num CPUs * 2) + 1
DJANGO_WSGI_MODULE=hines.config.wsgi             # WSGI module name

# Logging settings

LOG_LEVEL="info"
ACCESS_LOG_FILE=/webapps/hines/logs/gunicorn-access.log
ERROR_LOG_FILE=/webapps/hines/logs/gunicorn-error.log


echo "Starting $NAME as `whoami`"

# Activate the virtual environment
cd $DJANGODIR
source venv/bin/activate
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec venv/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user $USER \
  --group $GROUP \
  --bind unix:$SOCKFILE \
  --max-requests 1000 \
  --max-requests-jitter 50 \
  --log-level $LOG_LEVEL \
  --access-logfile $ACCESS_LOG_FILE \
  --error-logfile $ERROR_LOG_FILE \
  --capture-output  # Sends Django output to the logs
