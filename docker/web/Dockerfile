# Used for both web and djangoq

FROM python:3.10-slim-bullseye

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1

RUN apt-get update \
    && apt-get install -y build-essential git libpq-dev --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
    && apt-get clean

RUN pip install --upgrade pip-tools

RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip-sync

COPY . /code/
