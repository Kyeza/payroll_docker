# Base Image
FROM python:3.12.5-slim-bullseye
MAINTAINER Kyeza M. Arnold

# set default environment variables
ENV PYTHONUNBUFFERED 1
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

# install mysql dependencies
RUN apt-get update
RUN apt-get install python3-dev default-libmysqlclient-dev build-essential pkg-config -y

# install WeasyPrint dependencies
RUN apt-get install -y libpangocairo-1.0-0 -y

# install dependencies
RUN pip install -U pip setuptools wheel
RUN pip install --upgrade pip
COPY ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt --no-cache-dir

# create and set working directory
RUN mkdir /hr_system
WORKDIR /hr_system

RUN groupadd -r celery && useradd --no-log-init -r -g celery celery

# Add current directory code to working directory
ADD . /hr_system/

# Convert plain text files from Windows or Mac format to Unix
RUN apt-get install dos2unix
RUN dos2unix --newfile docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

# Make entrypoint executable
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Entrypoint dependencies
RUN apt-get update && apt-get install -y netcat-openbsd

# run entrypoint.sh
ENTRYPOINT ["bash", "/usr/local/bin/docker-entrypoint.sh"]
