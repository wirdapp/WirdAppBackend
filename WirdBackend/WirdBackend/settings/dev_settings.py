from .settings import *

DEBUG = True
SECRET_KEY = get_random_secret_key()

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny'
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'EXCEPTION_HANDLER': 'core.global_exception_handler.custom_exception_handler',
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
ALLOWED_HOSTS = ['*']
CORS_ALLOWED_ORIGINS = ["*"]
SECURE_HSTS_PRELOAD = False
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_PROXY_SSL_HEADER = None
SECURE_HSTS_SECONDS = 2_592_000
# Application definition
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False
X_FRAME_OPTIONS = 'Allow'
PERMISSIONS_POLICY = ["*"]
SESSION_COOKIE_HTTPONLY = False
SESSION_ENGINE = "django.contrib.sessions.models.Session"
