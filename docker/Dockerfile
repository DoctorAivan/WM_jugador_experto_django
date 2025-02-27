FROM python:3.12-alpine

ENV PYTHONUNBUFFERED=1

WORKDIR /
COPY ./requirements.txt .
RUN pip install -r requirements.txt && pip install gunicorn gevent

WORKDIR /app
COPY . .

EXPOSE 80

# Run migrations and server at entrypoint
ENTRYPOINT ./docker/entrypoint.sh
