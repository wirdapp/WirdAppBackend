import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', "123")

DEBUG = False

ALLOWED_HOSTS = []

# CORS & CSRF
CORS_ALLOW_CREDENTIALS = True
TRUSTED_ORIGINS = []
CSRF_TRUSTED_ORIGINS = []
CORS_ALLOWED_ORIGINS = []

# Core apps - always installed
INSTALLED_APPS = [
    'django.contrib.sessions',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.postgres',
    'django.contrib.sites',
    'member_panel.apps.StudentConfig',
    'admin_panel.apps.AdminPanelConfig',
    'core.apps.CoreConfig',
    'rest_framework',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'auth_kit',
    'auth_kit.social',

    'django_filters',
    'corsheaders',
    'polymorphic',
    'cachalot',
    'notifications',
    'django_q',
]

# Base middleware
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_permissions_policy.PermissionsPolicyMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'WirdBackend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

# Database
DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DATABASE_ENGINE"),
        "NAME": os.environ.get("DATABASE_NAME"),
        "USER": os.environ.get("DATABASE_USER"),
        "PASSWORD": os.environ.get("DATABASE_PASSWORD"),
        "HOST": os.environ.get("DATABASE_HOST"),
        "PORT": os.environ.get("DATABASE_PORT"),
        "CONN_MAX_AGE": 60,
        "CONN_HEALTH_CHECKS": True,
    }
}

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': f"redis://{os.environ.get('REDIS_URL', '127.0.0.1')}:{os.environ.get('REDIS_PORT', '6379')}",
        'TIMEOUT': 60,
    }
}

# Session engine — cached_db for fast reads (Redis) with DB fallback.
# Required for allauth social login (OAuth state + PKCE verifier storage).
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

# REST Framework — stateless by default
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'auth_kit.authentication.JWTCookieAuthentication',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FileUploadParser',
    ),
    'EXCEPTION_HANDLER': 'core.global_exception_handler.custom_exception_handler',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '300/day',
        'user': '50/minute',
    },
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'large': {
            'format': '%(asctime)s, %(levelname)s, %(filename)s, %(funcName)s, LineNo %(lineno)d : %(message)s',
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': '/var/log/wird_app/backend.log',
            'when': 'D',
            'backupCount': 30,
            'interval': 1,
            'formatter': 'large',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': os.environ.get("LOGGING_LEVEL", "INFO"),
            'propagate': True,
        },
        'django.request': {
            'handlers': ['file'],
            'level': os.environ.get("LOGGING_LEVEL", "INFO"),
            'propagate': True,
        },
        'django_q': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['file'],
        'level': os.environ.get("LOGGING_LEVEL", "INFO"),
        'propagate': True,
    },
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        'OPTIONS': {
            'max_similarity': 0.8,
            'user_attributes': ['username', 'first_name', 'last_name', 'email', 'phone_number'],
        },
    },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Auth Kit
AUTH_KIT = {
    'SOCIAL_LOGIN_AUTH_TYPE': 'code',
    'REGISTER_SERIALIZER': 'core.serializers.CustomRegisterSerializer',
    'USER_SERIALIZER': 'core.serializers.PersonSerializer',
    'USE_AUTH_COOKIE': False,
    'SOCIAL_LOGIN_CALLBACK_URL_GENERATOR': 'core.util_methods.get_social_callback_url',
}

# Social account providers
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'OAUTH_PKCE_ENABLED': True,
        'FETCH_USERINFO': True,
    }
}

# Internationalization
LANGUAGE_CODE = 'en'
LANGUAGES = [
    ('ar', _('Arabic')),
    ('en', _('English')),
]
LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]
USE_I18N = True
USE_TZ = True
TIME_ZONE = "Asia/Amman"

# Static files
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'core.Person'

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get("EMAIL_HOST_SMTP")
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = 'Wird App <no-reply@wird.app>'

# Cookie security defaults
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
# Cross-subdomain cookies — required for allauth OAuth redirects
# (Google/Facebook redirect back to a different subdomain than the one that started the flow)
SESSION_COOKIE_DOMAIN = ".wird.app"
CSRF_COOKIE_DOMAIN = ".wird.app"
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

# Security headers
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 2_592_000  # 30 days
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
X_FRAME_OPTIONS = 'DENY'
PERMISSIONS_POLICY = {"fullscreen": "*"}

# Upload limits
DATA_UPLOAD_MAX_MEMORY_SIZE = 5_242_880  # 5 MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 100

SITE_ID = int(os.getenv('DJANGO_SITE_ID', 1))

# Allauth
ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_UNIQUE_EMAIL = False
ACCOUNT_EMAIL_SUBJECT_PREFIX = "Wird Platform"
ACCOUNT_USERNAME_BLACKLIST = [
    "wird", "wirdapp", "wirduser", "wirdadmin", "wird_admin",
    "wird_user", "admin", "wird_app",
]
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = False
ACCOUNT_SIGNUP_REDIRECT_URL = "/"

# Firebase
FIREBASE_CREDENTIALS_PATH = os.environ.get('FIREBASE_CREDENTIALS_PATH', 'firebase_credentials.json')

# Django-Q task queue
Q_CLUSTER = {
    'name': 'wird_app',
    'workers': 1,
    'recycle': 500,
    'timeout': 60,
    'retry': 120,
    'queue_limit': 50,
    'bulk': 10,
    'catch_up': False,
    'max_attempts': 3,
    'logging': False,
}

# Cachalot
CACHALOT_TIMEOUT = 300  # 5 minutes

# ---------------------------------------------------------------------------
# GUI / Admin helpers
# Controls DRF browsable API, Django Admin, and static files.
# Session infrastructure is always active for allauth social login.
# ---------------------------------------------------------------------------
ENABLE_GUI = os.environ.get('ENABLE_GUI', 'false') == 'true'
ENABLE_ADMIN = os.environ.get('ENABLE_ADMIN', 'false') == 'true'

if ENABLE_ADMIN:
    INSTALLED_APPS = ['django.contrib.admin'] + INSTALLED_APPS

if ENABLE_GUI or ENABLE_ADMIN:
    INSTALLED_APPS = ['django.contrib.staticfiles'] + INSTALLED_APPS
    REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = [
        'rest_framework.authentication.SessionAuthentication',
        'auth_kit.authentication.JWTCookieAuthentication',
    ]
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ]
