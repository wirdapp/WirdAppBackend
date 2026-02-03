from .settings import *

DEBUG = False

ALLOWED_HOSTS = ["localhost", '0.0.0.0', 'api.wird.app', "admin.wird.app", "wird.app"]

TRUSTED_ORIGINS = [
    "https://api.wird.app",
    "https://admin.wird.app",
    "https://wird.app",
    "https://www.wird.app",
]
CSRF_TRUSTED_ORIGINS = TRUSTED_ORIGINS
CORS_ALLOWED_ORIGINS = TRUSTED_ORIGINS

# Production logging
LOGGING['loggers']['django']['level'] = os.environ.get("LOGGING_LEVEL", "WARNING")
LOGGING['loggers']['django.request']['level'] = os.environ.get("LOGGING_LEVEL", "WARNING")
LOGGING['root']['level'] = os.environ.get("LOGGING_LEVEL", "WARNING")

# Strict security
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
Q_CLUSTER.update({
    'workers': 4,
    'queue_limit': 100,
    'redis': {
        'host': os.environ.get('REDIS_URL', '127.0.0.1'),
        'port': os.environ.get('REDIS_PORT', '6379'),
        'db': 1
    },
})
