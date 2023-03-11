import os


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1234'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'd9bdahiujnd5gs',
        'USER': 'ggjhmrunathqpt',
        'PASSWORD': '8d6b511a735a9151291cea7dcbd2815296b4daf0889f066ff477db55aabd8c60',
        'HOST': 'ec2-52-208-185-143.eu-west-1.compute.amazonaws.com',
        'PORT': '5432',
        'URI': 'postgres://ggjhmrunathqpt:8d6b511a735a9151291cea7dcbd2815296b4daf0889f066ff477db55aabd8c60@ec2-52-208-185-143.eu-west-1.compute.amazonaws.com:5432/d9bdahiujnd5gs'
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
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',  # TODO REMOVE
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
}

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
