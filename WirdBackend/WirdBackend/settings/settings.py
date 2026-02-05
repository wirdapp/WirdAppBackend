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
    'django.contrib.postgres',
    'django.contrib.sites',
    'member_panel.apps.StudentConfig',
    'admin_panel.apps.AdminPanelConfig',
    'core.apps.CoreConfig',
    'rest_framework',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',  # Google OAuth2
    'allauth.socialaccount.providers.facebook',  # Facebook OAuth2
    'allauth.socialaccount.providers.instagram',  # Instagram OAuth2
    # 'allauth.socialaccount.providers.apple',
    'auth_kit',
    'auth_kit.social',  # DRF Auth Kit social integration

    'django_filters',
    'corsheaders',
    'polymorphic',
    'cachalot',
    'notifications',
    'django_q'
]

# Base middleware
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
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
    }
}

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': f"redis://{os.environ.get('REDIS_URL', '127.0.0.1')}:{os.environ.get('REDIS_PORT', '6379')}",
        'TIMEOUT': 60
    }
}

# REST Framework - Stateless by default
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'
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
        'rest_framework.parsers.FileUploadParser'
    ),
    'EXCEPTION_HANDLER': 'core.global_exception_handler.custom_exception_handler',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
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
            'format': '%(asctime)s, %(levelname)s, %(filename)s, %(funcName)s, LineNo %(lineno)d : %(message)s'
        },
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
            'level': os.environ.get("LOGGING_LEVEL", "INFO"),
            'propagate': True,
        },
        'django.request': {
            'handlers': ['file'],
            'level': os.environ.get("LOGGING_LEVEL", "INFO"),
            'propagate': True,
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
            'user_attributes': ['username', 'first_name', 'last_name', 'email', 'phone_number']
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

AUTH_KIT = {
    'SOCIAL_LOGIN_AUTH_TYPE': 'code',  # Recommended: 'code' for security, or 'token'
    "USER_SERIALIZER": "core.serializers.PersonSerializer",
    "USE_AUTH_COOKIE": False,
    "SOCIAL_LOGIN_CALLBACK_URL_GENERATOR": "core.util_methods.get_social_callback_url",
}

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'OAUTH_PKCE_ENABLED': True,
        'FETCH_USERINFO': True,
    },
    'facebook': {
        'METHOD': 'oauth2',  # Set to 'js_sdk' if using the Facebook JS SDK
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'INIT_PARAMS': {'cookie': True},
        'FIELDS': [
            'id',
            'first_name',
            'last_name',
            'middle_name',
            'name',
            'name_format',
            'picture',
            'short_name',
            'email',
        ],
        'EXCHANGE_TOKEN': True,
        'VERIFIED_EMAIL': False,
        'VERSION': 'v13.0',  # Use the latest Graph API version
    },
    'instagram': {
        'SCOPE': ['user_profile', 'user_media'],
        'AUTH_PARAMS': {'access_type': 'online'},
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
USE_L10N = False
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

# Security Headers
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 2_592_000
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
PERMISSIONS_POLICY = {"fullscreen": "*"}

SITE_ID = int(os.getenv('DJANGO_SITE_ID', 1))

# Allauth
ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_UNIQUE_EMAIL = False
ACCOUNT_EMAIL_SUBJECT_PREFIX = "Wird Platform"
ACCOUNT_USERNAME_BLACKLIST = ["wird", "wirdapp", "wirduser", "wirdadmin", "wird_admin", "wird_user", "admin",
                              "wird_app"]
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = False
ACCOUNT_SIGNUP_REDIRECT_URL = "/"
# Firebase Configuration
FIREBASE_CREDENTIALS_PATH = os.environ.get('FIREBASE_CREDENTIALS_PATH', 'firebase_credentials.json')

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
}
