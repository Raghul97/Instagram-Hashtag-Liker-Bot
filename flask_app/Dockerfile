FROM python:3.8-slim

# installing required packages.
COPY requirements.freeze /
RUN pip install -r /requirements.freeze

# copy all source files.
ADD . /flask_app
WORKDIR /flask_app

# setting required environment.
ENV FLASK_ENV=development
ENV FLASK_APP=app.py

# run flask at port 5000.
CMD flask run --host=0.0.0.0