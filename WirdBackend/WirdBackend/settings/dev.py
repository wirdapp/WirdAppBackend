from .settings import *

DEBUG = True

ALLOWED_HOSTS = ["localhost", '0.0.0.0', 'dev-api.wird.app', "dev-admin.wird.app", "dev.wird.app"]

TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:8000",
    "http://localhost:8200",
    "https://dev-api.wird.app",
    "https://dev-admin.wird.app",
    "https://dev.wird.app",
    "https://dev-www.wird.app",
]
CSRF_TRUSTED_ORIGINS = TRUSTED_ORIGINS
CORS_ALLOWED_ORIGINS = TRUSTED_ORIGINS
CORS_ALLOW_ALL_ORIGINS = True

ENABLE_API_DOCS = True
INSTALLED_APPS = ['drf_spectacular'] + INSTALLED_APPS

# Relaxed password rules for dev
AUTH_PASSWORD_VALIDATORS = []
ACCOUNT_PASSWORD_MIN_LENGTH = 1

# Disable rate limiting
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {}

# API docs
REST_FRAMEWORK['DEFAULT_SCHEMA_CLASS'] = 'drf_spectacular.openapi.AutoSchema'
SPECTACULAR_SETTINGS = {
    'TITLE': 'Wird APIs',
    'DESCRIPTION': 'Wird endpoints documentation',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# Verbose logging for dev
LOGGING['loggers']['django']['level'] = 'INFO'
LOGGING['loggers']['django.request']['level'] = 'INFO'
LOGGING['root']['level'] = 'INFO'

Q_CLUSTER.update({
    'orm': 'default',
})

AUTH_KIT["SOCIAL_HIDE_AUTH_ERROR_DETAILS"] = False
