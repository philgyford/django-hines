FROM python:3.9-slim-bullseye

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1

RUN apt-get update \
    && apt-get install -y build-essential git libpq-dev --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
    && apt-get clean

RUN mkdir /code
WORKDIR /code

RUN pip install --upgrade pipenv
COPY ./Pipfile .
COPY ./Pipfile.lock .
RUN pipenv install --dev --deploy
