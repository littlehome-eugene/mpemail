"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = BASE_DIR
sys.path.append(os.path.join(PROJECT_DIR, 'apps'))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '92-=6fn+d5m-i9h(9%onza(e(jh^xv!%%-^q*p-qsd%(sp1pd)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_extensions',
    'django_celery_results',
    'corsheaders',

    'mpemail',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',


    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'mysite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }

    # 'default': {
    #     # 'ENGINE': 'django.contrib.gis.db.backends.postgis',
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #     'NAME': 'mpemail',                      # Or path to database file if using sqlite3.
    #     'USER': 'mpemail',                      # Not used with sqlite3.
    #     'PASSWORD': 'mpemail',                  # Not used with sqlite3.
    #     'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
    #     'PORT': '5432',                      # Set to empty string for default. Not used with sqlite3.
    #     'CONN_MAX_AGE': 60,
    # },

}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

MAILPILE_URL = 'http://127.0.0.1:10033'

CELERY_RESULT_BACKEND = 'django-db'

CORS_ORIGIN_ALLOW_ALL = True

ALLOWED_HOSTS = ['*']



MEDIA_URL = "media/"



if DEBUG:
    CELERY_TASK_ALWAYS_EAGER = True


OUTPUT_DIR = os.path.join(BASE_DIR, 'output')


EMAIL_SENDER = 'test@natureprime.co.kr'
EMAIL_SENDER_NAME = 'Sales'

DATA_DIR = os.path.join(BASE_DIR, 'data')

LOG_DIR = os.path.join(BASE_DIR, 'log')


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'myproject.log'),
            'when': 'midnight', # this specifies the interval
            'interval': 1, # defaults to 1, only necessary for other values
            'backupCount': 365*10, # how many backup file to keep, 365 days
            'formatter': 'verbose',
        },

        # 'null': {
        #     'level': 'DEBUG',
        #     'class': 'django.utils.log.NullHandler',
        # },
        # # 'console': {
        #     'level': 'INFO',
        #     'class': 'logging.StreamHandler',
        #     'formatter': 'simple'
        # },

    },
    'loggers': {
        # 'django': {
        #     'handlers': ['file'],
        #     'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        # },
        # 'django': {
        #     'handlers': ['console'],
        #     'propagate': True,
        # },
        'my': {
            'handlers': ['file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        }
    },
}