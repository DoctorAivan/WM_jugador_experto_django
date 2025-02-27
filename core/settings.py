"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 4.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import os, sys
from dotenv import load_dotenv
from pathlib import Path

#       #       #       #       #       #       #       #       #       #       #       #       #
# ENVIROMMENT VARIABLES

STAGE = os.getenv('STAGE', "DEV")  # (dev, production)
STAGE = STAGE.upper()

# ENV Django
if STAGE == "DEV":
    DEBUG = True
    load_dotenv("development.env")
elif STAGE == "PRODUCTION":
    DEBUG = False

SECRET_KEY = os.getenv('SECRET_KEY')

# Load variables
# Production load variables from remote env file specified in zappa_settings.json
if STAGE == "PRODUCTION":
    DEBUG = False
else:
    DEBUG = True
    load_dotenv("development.env")

# ENV Database
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

# ENV Redis
REDIS_LOCATION = os.getenv('REDIS_LOCATION')
REDIS_KEY_PREFIX = os.getenv('REDIS_KEY_PREFIX')

#       #       #       #       #       #       #       #       #       #       #       #       #

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "access-control-allow-origin",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# CORS definitions
if STAGE == "PRODUCTION":
    CORS_ALLOW_ALL_ORIGINS = False

    CORS_ORIGIN_WHITELIST = (
        'http://localhost:5173',  # FIXME: Remove this line
    )

    CORS_ALLOWED_ORIGINS = [
        'http://localhost:5173',  # FIXME: Remove this line
    ]
    for host in os.getenv('ALLOWED_HOSTS').split(","):
        CORS_ORIGIN_WHITELIST += ('https://{}'.format(host),)
        CORS_ALLOWED_ORIGINS += ('https://{}'.format(host),)

    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(",")

if STAGE == "DEV":
    CORS_ALLOW_ALL_ORIGINS = True

    CORS_ORIGIN_WHITELIST = (
        'http://localhost:5173',
        'http://192.168.1.100:5173',
    )

    CORS_ALLOWED_ORIGINS = [
        'http://localhost:5173',
        'http://127.0.0.1:5173',
        'http://192.168.1.100:5173',
    ]

    ALLOWED_HOSTS = [
        'localhost',
        '127.0.0.1',
        '192.168.1.100',
    ]
    ALLOWED_HOSTS.extend(os.getenv('ALLOWED_HOSTS').split(","))

# Application definition
INSTALLED_APPS = [

    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Libs
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',

    # Apps
    'apps.api'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

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

WSGI_APPLICATION = 'core.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
    }
}

# Redis caches
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_LOCATION,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': REDIS_KEY_PREFIX
    }
}

# Optional: Configuration to avoid using the database as a fallback
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

if STAGE == "PRODUCTION":
    REST_FRAMEWORK = {
        'DEFAULT_RENDERER_CLASSES': (
            'rest_framework.renderers.JSONRenderer',
        ),
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework.authentication.SessionAuthentication',
            'rest_framework.authentication.TokenAuthentication',
        ),
#       'DEFAULT_THROTTLE_RATES': {
#           'user': '1000/hour',
#           'anon': '100/hour',
#       },
    }
else:
    REST_FRAMEWORK = {
        'DEFAULT_RENDERER_CLASSES': (
            'rest_framework.renderers.JSONRenderer',
        ),
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework.authentication.SessionAuthentication',
            'rest_framework.authentication.TokenAuthentication',
        ),
    }

# TESTING flag to bypass some code in testing like captcha
TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'

# Minimun players in scheme
MIN_SCHEME = 3
APPEND_SLASH = False
