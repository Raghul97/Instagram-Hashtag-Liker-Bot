FROM python:3.8-alpine

ENV PYTHONUNBUFFERED 1

# install required packages.
COPY ./requirements.freeze /requirements.freeze
RUN pip install -r requirements.freeze

# copy source files in the current directory.
ADD . /celery_worker
WORKDIR /celery_worker

# executing celery worker with taskname and celery app name.
ENTRYPOINT celery -A tasks.app worker --loglevel=info --statedb=/var/worker.state
