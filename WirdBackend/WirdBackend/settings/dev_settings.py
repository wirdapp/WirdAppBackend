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
        'dj_rest_auth.jwt_auth.JWTCookieAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'EXCEPTION_HANDLER': 'core.global_exception_handler.custom_exception_handler',
}

INSTALLED_APPS = [
    "django.contrib.messages",
    'django.contrib.admin',
    'django.contrib.sessions',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    "django.contrib.postgres",
    'member_panel.apps.StudentConfig',
    'admin_panel.apps.AdminPanelConfig',
    'core.apps.CoreConfig',
    'rest_framework',
    "rest_framework.authtoken",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    'django_filters',
    'corsheaders',
    'polymorphic',
    'drf_yasg',
    "cachalot",
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ALLOWED_HOSTS = [
    'localhost',
    '0.0.0.0',
    "dev.wird.app",
    'admin.wird.app',
    'admin.wird.app',
    "api_dev.wird.app",
    "admin_dev.wird.app",
]
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:8080',
    'http://localhost:8000',
    'https://admin.wird.app',
    'https://api_dev.wird.app',
    "https://admin_dev.wird.app"
]
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:8080',
    'http://localhost:8000',
    'https://admin.wird.app',
    'https://api_dev.wird.app',
    "https://admin_dev.wird.app"
]
