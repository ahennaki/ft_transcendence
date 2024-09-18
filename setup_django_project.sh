#!/bin/bash
# Script for automating the setup of a Django project, and creating a virtual env, a Django app
# and containerize the project using a Dockerfile

# TODO: Configure settings

# Check if the project name was provided
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Please provide both a project name and an app name."
    exit 1
fi

PROJECT_NAME=$1
APP_NAME=$2

# Check if the project already exists
if [ -d "$PROJECT_NAME" ]; then
    echo "Project $PROJECT_NAME already exists."
    exit 1
fi

# export env variables 
# if [ "$ENV" == "production" ]; then
#     ENV_FILE="Manage_services/.envProduction"
#     cp "$ENV_FILE" "Manage_services/.env"
# else
#     ENV_FILE="Manage_services/.envDevelopment"
#     cp "$ENV_FILE" "Manage_services/.env"
# fi

# set -a
# source $ENV_FILE
# set +a

# Create project directory
mkdir "$PROJECT_NAME"
cd "$PROJECT_NAME"


# Create virtual environment and install Django and other dependencies
pipenv install \
    django~=5.0 \
    djangorestframework~=3.15.0 \
    # djangorestframework-simplejwt \
    # django-oauth-toolkit \
    django-cors-headers \
    python-memcached \
    postgres \
    psycopg2-binary \
    # pyjwt \
    # django-two-factor-auth[phonenumbers] \
    # django-otp \
    # qrcode \

# Create Django Project
pipenv run django-admin startproject config .

# Create Django app
pipenv run python3 manage.py startapp "$APP_NAME"

# Create requirements file
pipenv run pip3 freeze > requirements.txt

# Create Dockerfile
cat > Dockerfile <<EOF
FROM python:3.11.9-bookworm

RUN apt-get update

ENV PYTHONDONTWRITEBYTECODE TRUE
ENV PYTHONUNBUFFERED TRUE

WORKDIR /app

RUN pip install --upgrade pip
COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app/

EXPOSE 8000

CMD [ "bash", "-c", "python3 manage.py makemigrations && python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:8000" ]
EOF
