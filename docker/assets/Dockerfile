# pull official base image
FROM python:3.8-alpine

RUN apk update \
    && apk add --no-cache \
    git \
    # For front-end build:
    nodejs yarn

# set work directory
RUN mkdir /code
WORKDIR /code

# For front-end build:
COPY package.json yarn.lock gulpfile.js /code/
RUN yarn install

# copy project
COPY . /code/

# Run gulp to build static assets in image
RUN yarn build