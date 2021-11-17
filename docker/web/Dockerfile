# pull official base image
FROM python:3.8-alpine

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1
ENV PYTHONUNBUFFERED 1

RUN apk update \
    && apk add --no-cache \
    git \
    # Required for installing/upgrading postgres and Pillow:
    gcc python3-dev \
    # Required for installing/upgrading postgres:
    postgresql-libs postgresql-dev musl-dev \
    # Required for installing/upgrading Pillow:
    jpeg-dev zlib-dev libjpeg \
    # Because?
    postgresql-client \
    # For front-end build:
    nodejs \
    yarn

# set work directory
RUN mkdir /code
WORKDIR /code

# install dependencies
RUN pip install --upgrade pipenv
COPY ./Pipfile .
COPY ./Pipfile.lock .
RUN pipenv install --dev --deploy

# For front-end build:
COPY package.json yarn.lock gulpfile.js /code/
RUN yarn install

# copy project
COPY . /code/

# Run gulp to build static assets in image
RUN yarn build
