"""
Django settings for Ramadan_Competition_Rest project.

Generated by 'django-admin startproject' using Django 4.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
import os

try:
    SECRET_KEY = os.environ["SECRET_KEY"]
except KeyError as e:
    raise RuntimeError("Could not find a SECRET_KEY in environment") from e

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': 'localhost',
        'NAME': 'ramadan_comp',
        'USER': 'osama',
        'PASSWORD': SECRET_KEY,
        'PORT': '5432',
        'CONN_MAX_AGE': 60,
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379',
        'TIMEOUT': 60
    }
}

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAdminUser'
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'EXCEPTION_HANDLER': 'core.global_exception_handler.custom_exception_handler',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '300/day',
        'user': '30/minute'
    },
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'large': {
            'format': '%(asctime)s, %(levelname)s, %(filename)s, %(funcName)s, LineNo %(lineno)d : %(message)s'
        },
        'tiny': {
            'format': '%(asctime)s %(message)s  '
        }
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': f'{os.environ.get("HOME")}/backend_log/backend.log',
            'when': 'D',
            'backupCount': 5,
            'interval': 1,
            'formatter': 'large'
        },
    },
    'console': {
        'level': 'DEBUG',
        'formatter': 'tiny',
        'class': 'logging.StreamHandler',
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'DEBUG',
    },
}

CORS_ALLOWED_ORIGINS = ["http://localhost", 'http://0.0.0.0', 'https://student.wird.app', 'https://admin.wird.app',
                        'https://ramadan-comp-rest.herokuapp.com']