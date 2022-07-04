#!/bin/bash
# Name of the application
NAME="sso"
# Django project directory
DJANGODIR=/root/server/sso
# we will communicte using this unix socket
SOCKFILE=/root/server/sso/gunicorn.sock
# the user to run as
USER=root
# the group to run as
GROUP=root
# how many worker processes should Gunicorn spawn
NUM_WORKERS=3
# which settings file should Django use
DJANGO_SETTINGS_MODULE=sso.settings
# WSGI module name
DJANGO_WSGI_MODULE=sso.wsgi
echo "Starting $NAME as `whoami`"
# Activate the virtual environment
cd $DJANGODIR
source /root/server/sso/venv/bin/activate

export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR
# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)

exec /root/server/sso/venv/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
--name $NAME \
--workers $NUM_WORKERS \
--user=$USER --group=$GROUP \
--bind=localhost:8000 \
--log-level=debug \
--log-file=-
