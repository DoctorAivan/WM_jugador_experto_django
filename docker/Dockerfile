FROM python:3.9-alpine

ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY ./requirements.txt .

RUN pip install -r requirements.txt && pip install gunicorn gevent

# Run migrations and server at entrypoint
ENTRYPOINT ./docker/entrypoint.sh
