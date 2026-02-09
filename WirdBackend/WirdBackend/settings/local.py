from .dev import *

ALLOWED_HOSTS = ["*"]

TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:8000",
    "http://localhost:8200",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8200",
]
CSRF_TRUSTED_ORIGINS = TRUSTED_ORIGINS
CORS_ALLOWED_ORIGINS = TRUSTED_ORIGINS

# Local database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'wird_local'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Dummy cache — no Redis needed locally
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Fall back to pure DB sessions since there's no Redis locally
SESSION_ENGINE = "django.contrib.sessions.backends.db"

# Cachalot is useless with DummyCache
CACHALOT_ENABLED = False

# Console email
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# No security for local development
SECURE_HSTS_SECONDS = 0
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_DOMAIN = None
CSRF_COOKIE_DOMAIN = None
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

# Console logging
LOGGING['handlers'] = {
    'console': {
        'class': 'logging.StreamHandler',
        'formatter': 'large',
    }
}
LOGGING['loggers']['django']['handlers'] = ['console']
LOGGING['loggers']['django.request']['handlers'] = ['console']
LOGGING['loggers']['django_q']['handlers'] = ['console']
LOGGING['root']['handlers'] = ['console']

SITE_ID = 2