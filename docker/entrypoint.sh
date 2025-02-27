#!/bin/sh

# If env PRODUCTION is 1, then run the production server, otherwise if its 0 run the development server
if [ "$STAGE" = "PRODUCTION" ]; then
  # Run the production server
  # -k daphne
  gunicorn -w 8 \
      -k gevent \
      --worker-connections 1000 \
      --bind :80 \
      core.wsgi:application
      
elif [ "$STAGE" = "DEV" ]; then
  # Run the development server
  python manage.py runserver 0.0.0.0:8000
fi

