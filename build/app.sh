#!/bin/sh
# main application entrypoint

if [ "$FLASK_ENV" == "development" ]; then
	# use flask debug server in development
	exec /usr/local/bin/website app
else
	# use gunicorn in production
	exec gunicorn --workers $GUNICORN_WORKERS --bind :8080 --chdir /opt netsoc:app
fi
