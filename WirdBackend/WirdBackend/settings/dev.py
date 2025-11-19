from .settings import *

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
DEBUG = True

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = False  # nginx already redirects 80 -> 443
SECURE_HSTS_SECONDS = 0
# GUI mode for dev server
ENABLE_GUI = os.environ.get('ENABLE_GUI', 'true').lower() == 'true'
ENABLE_ADMIN = os.environ.get('ENABLE_ADMIN', 'true').lower() == 'true'
ENABLE_API_DOCS = True

INSTALLED_APPS = ['drf_spectacular'] + INSTALLED_APPS

if ENABLE_ADMIN:
    INSTALLED_APPS = ['django.contrib.admin', 'django.contrib.messages'] + INSTALLED_APPS

if ENABLE_GUI or ENABLE_ADMIN:
    MIDDLEWARE.insert(5, 'django.contrib.sessions.middleware.SessionMiddleware')
    MIDDLEWARE.insert(6, 'django.contrib.auth.middleware.AuthenticationMiddleware')
    MIDDLEWARE.insert(7, 'django.contrib.messages.middleware.MessageMiddleware')
    # Add session authentication + browsable API
    REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = [
        'rest_framework.authentication.SessionAuthentication',
        'auth_kit.authentication.JWTCookieAuthentication',
    ]
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ]
    # Enable sessions
    SESSION_ENGINE = "django.contrib.sessions.backends.db"
    INSTALLED_APPS = ["django.contrib.staticfiles"] + INSTALLED_APPS

AUTH_PASSWORD_VALIDATORS = []
ACCOUNT_PASSWORD_MIN_LENGTH = 1
# Disable rate limiting
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {}

# Add schema class
REST_FRAMEWORK['DEFAULT_SCHEMA_CLASS'] = 'drf_spectacular.openapi.AutoSchema'

# Spectacular settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'Wird APIs',
    'DESCRIPTION': 'Wird endpoints documentation',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# More verbose logging
LOGGING['loggers']['django']['level'] = 'INFO'
LOGGING['loggers']['django.request']['level'] = 'INFO'
LOGGING['root']['level'] = 'INFO'

# Less strict security
SECURE_HSTS_SECONDS = 60
