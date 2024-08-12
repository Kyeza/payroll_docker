"""
Django settings for hr_system project.

Generated by 'django-admin startproject' using Django 2.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import json

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from celery.schedules import crontab

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-#&")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.environ.get("DEBUG", default=0))

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(" ")

# Application definition

INSTALLED_APPS = [
    'users.apps.UsersConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'payroll.apps.PayrollConfig',
    'support_data.apps.SupportDataConfig',
    'reports.apps.ReportsConfig',
    'crispy_forms',
    'crispy_bootstrap4',
    'bootstrap4',
    'debug_toolbar',
    'django.contrib.sites',
    'django_celery_results',
    'django_celery_beat',
    'djcelery_email',
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
]

INTERNAL_IPS = ['127.0.0.1']

ROOT_URLCONF = 'hr_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'hr_system.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

# [START db_setup]
if os.getenv('GAE_APPLICATION', None):
    # Running on production App Engine, so connect to Google Cloud SQL using
    # the unix socket at /cloudsql/<your-cloudsql-connection string>
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'HOST': '/cloudsql/payroll-236416:us-central1:payroll-instance',
            'USER': 'root',
            'PASSWORD': '',
            'NAME': 'payroll_schema',
        }
    }
else:
    # Running locally so connect to either a local MySQL instance or connect to
    # Cloud SQL via the proxy. To start the proxy via command line:
    #
    #     $ cloud_sql_proxy -instances=[INSTANCE_CONNECTION_NAME]=tcp:3306
    #
    # See https://cloud.google.com/sql/docs/mysql-connect-proxy

    DATABASES = {
        "default": {
            "ENGINE": os.environ.get("SQL_ENGINE", "django.db.backends.sqlite3"),
            "OPTIONS": json.loads(os.environ.get("SQL_OPTIONS", "{}")),
            "NAME": os.environ.get("SQL_DATABASE", os.path.join(BASE_DIR, 'db.sqlite3')),
            "USER": os.environ.get("SQL_USER", "myuser"),
            "PASSWORD": os.environ.get("SQL_PASSWORD", "myuserpassword"),
            "HOST": os.environ.get("SQL_HOST", "localhost"),
            "PORT": os.environ.get("SQL_PORT", "3306"),
        }
    }
# [END db_setup]


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"
CRISPY_TEMPLATE_PACK = 'bootstrap4'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

LOGIN_REDIRECT_URL = 'payroll:index'
LOGIN_URL = 'login'

LOGOUT_REDIRECT_URL = 'payroll:index'
LOGOUT_RESET_REDIRECT_URL = 'password_reset'

AUTH_USER_MODEL = 'users.User'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'payroll': {
            'handlers': ['console'],
            'level': 'DEBUG'
        }
    }
}


# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND')
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_USE_TLS = bool(os.getenv('EMAIL_USE_TLS'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')

CACHES = {
    'default': {
        'BACKEND': os.environ.get('CACHE_BACKEND', 'django.core.cache.backends.locmem.LocMemCache'),
        'LOCATION': os.environ.get('CACHE_LOCATION', 'unique-snowflake'),
    }
}

CACHE_MIDDLEWARE_ALIAS = os.environ.get('CACHE_MIDDLEWARE_ALIAS', 'default')
CACHE_MIDDLEWARE_SECONDS = os.environ.get('CACHE_MIDDLEWARE_SECONDS', 600)
CACHE_MIDDLEWARE_KEY_PREFIX = os.environ.get('CACHE_MIDDLEWARE_KEY_PREFIX', '')

CELERY_BROKER_URL = os.environ.get('BROKER_URL')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'django-db')
CELERYBEAT_SCHEDULER = os.environ.get('CELERYBEAT_SCHEDULER', 'django_celery_beat.schedulers:DatabaseScheduler')

# Other Celery settings
CELERY_BEAT_SCHEDULE = {
    'task-number-one': {
        'task': 'notify_user_on_contract_expiry',
        'schedule': crontab(hour=7, minute=30, day_of_week=1)
    }
}
