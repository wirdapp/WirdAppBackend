import os
from pathlib import Path

from django.core.management.utils import get_random_secret_key
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = get_random_secret_key()

DEBUG = False

ALLOWED_HOSTS = ["localhost", '0.0.0.0', 'api.wird.app', "admin.wird.app", "wird.app"]
CORS_ALLOW_CREDENTIALS = True
TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:8000",
    "https://api.wird.app",
    "https://admin.wird.app",
    "https://wird.app",
    "https://www.wird.app",
    "http://localhost:8200",
]
CSRF_TRUSTED_ORIGINS = TRUSTED_ORIGINS
CORS_ALLOWED_ORIGINS = TRUSTED_ORIGINS

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': f"redis://{os.environ.get('REDIS_URL', '127.0.0.1')}:{os.environ.get('REDIS_PORT', '6379')}",
        'TIMEOUT': 60
    }
}

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DATABASE_ENGINE"),
        "NAME": os.environ.get("DATABASE_NAME"),
        "USER": os.environ.get("DATABASE_USER"),
        "PASSWORD": os.environ.get("DATABASE_PASSWORD"),
        "HOST": os.environ.get("DATABASE_HOST"),
        "PORT": os.environ.get("DATABASE_PORT"),
        "CONN_MAX_AGE": 60,
    }
}

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'dj_rest_auth.jwt_auth.JWTCookieAuthentication',
    ],
    'EXCEPTION_HANDLER': 'core.global_exception_handler.custom_exception_handler',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '300/day',
        'user': '50/minute',
    },
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FileUploadParser"
    ),
}

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
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': '/var/log/wird_app/backend.log',
            'when': 'D',
            'backupCount': 30,
            'interval': 1,
            'formatter': 'large'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': os.environ.get("LOGGING_LEVEL"),
            'propagate': True,
        },
        'django.request': {
            'handlers': ['file'],
            'level': os.environ.get("LOGGING_LEVEL"),
            'propagate': True,
        },
    },
    'root': {
        'handlers': ['file'],
        'level': os.environ.get("LOGGING_LEVEL"),
        'propagate': True,
    },
}

INSTALLED_APPS = [
    # "django.contrib.messages",
    # 'django.contrib.admin',
    # 'django.contrib.sessions',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    "django.contrib.postgres",
    'member_panel.apps.StudentConfig',
    'admin_panel.apps.AdminPanelConfig',
    'core.apps.CoreConfig',
    'rest_framework',
    "rest_framework.authtoken",
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'dj_rest_auth.registration',
    'django_filters',
    'corsheaders',
    'polymorphic',
    'drf_yasg',
    "cachalot",
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "django_permissions_policy.PermissionsPolicyMiddleware",
    'django.middleware.locale.LocaleMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'WirdBackend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
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

WSGI_APPLICATION = 'WirdBackend.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        'OPTIONS': {
            'max_similarity': 0.8,
            "user_attributes": ["username", "first_name", "last_name", "email", "phone_number"]
        }
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

LANGUAGE_CODE = 'en'

LANGUAGES = [
    ('ar', _('Arabic')),
    ('en', _('English')),
]

LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale'), ]

USE_I18N = True

USE_TZ = True

USE_L10N = False

# STATIC_URL = '/static/'
# MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'core.Person'

# Email Backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get("EMAIL_HOST_SMTP")
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = 'Wird App <no-reply@wird.app>'

# Security Headers
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 2_592_000
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
# Application definition

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
PERMISSIONS_POLICY = {"fullscreen": "*", }
## For dj-rest-auth
REST_AUTH = {
    'USE_JWT': True,
    'JWT_AUTH_COOKIE': 'wird-jwt-auth',
    'JWT_AUTH_REFRESH_COOKIE': 'wird-jwt-refresh',
    'JWT_AUTH_RETURN_EXPIRATION': True,
    'JWT_AUTH_HTTPONLY': False,
    "SESSION_LOGIN": False,
    "USER_DETAILS_SERIALIZER": "core.serializers.PersonSerializer",
    "PASSWORD_RESET_SERIALIZER": "core.util_classes.PasswordResetSerializer"
}
SITE_ID = 1

# For Allauth
ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_UNIQUE_EMAIL = False
ACCOUNT_EMAIL_SUBJECT_PREFIX = "Wird Platform"
ACCOUNT_USERNAME_BLACKLIST = ["wird", "wirdapp", "wirduser", "wirdadmin", "wird_admin", "wird_user", "admin",
                              "wird_app"]
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = False
ACCOUNT_ADAPTER = "core.util_classes.AllAuthSessionLessAdapter"
ACCOUNT_SIGNUP_REDIRECT_URL = "/"
