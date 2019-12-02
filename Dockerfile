# Base Image
FROM python:3.7
MAINTAINER Kyeza M. Arnold

# set default environment variables
ENV PYTHONUNBUFFERED 1
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

COPY ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt

# create and set working directory
RUN mkdir /hr_system
WORKDIR /hr_system

RUN groupadd -r celery && useradd --no-log-init -r -g celery celery

# Add current directory code to working directory
ADD . /hr_system/
