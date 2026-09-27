from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

import os
import sys

sys.path.insert(0, os.path.join(BASE_DIR, "api"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", "False").lower() in ("1", "true", "yes")

ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get(
        "ALLOWED_HOSTS", "api.equb.equblinktrading.com,localhost,127.0.0.1"
    ).split(",")
    if h.strip()
]

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    if len(SECRET_KEY) < 50 or SECRET_KEY.startswith("django-insecure-"):
        raise ImproperlyConfigured(
            "DJANGO_SECRET_KEY must be at least 50 random characters in production."
        )

# Behind the TLS-terminating web server: trust its X-Forwarded-Proto so
# request.is_secure() / build_absolute_uri() produce https URLs.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "False").lower() in ("1", "true", "yes")
SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_HSTS_SECONDS > 0
SECURE_HSTS_PRELOAD = False

# Browser origins allowed to call the API (the owner panel). Comma-separated in .env.
CORS_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.environ.get("CORS_ALLOWED_ORIGINS", "https://equb-admin-panal.vercel.app").split(",")
    if o.strip()
]
if DEBUG:
    CORS_ALLOWED_ORIGINS += [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8081",
        "http://127.0.0.1:8081",
        "http://localhost:19006",
    ]

# Application definition

INSTALLED_APPS = [
    "jazzmin",
    "admin_interface",
    "colorfield",
    
    # old
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "drf_spectacular",
    "corsheaders",
    "django_filters",
    "django_cleanup.apps.CleanupConfig",
    "user",
    "advert",
    "equbApp",
    "owner_panel",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "equb.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "equb.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.mysql",
#         "NAME": "tuqualify_db",
#         "USER": "root",
#         "PASSWORD": "",
#         "HOST": "127.0.0.1",
#         "PORT": "3306",
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# STATIC_URL = 'static/'
# settings.py

STATIC_URL = "/equb/static/"  # This matches the location used in Nginx
STATIC_ROOT = os.path.join(
    BASE_DIR, "static"
)  # Or another path where you want to collect static files


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
#  get the Account model from user app
AUTH_USER_MODEL = "user.Account"

MEDIA_ROOT = os.path.join(BASE_DIR, "media/")  # 'data' is my media folder
MEDIA_URL = "/media/"


# Rest API authentication type
REST_FRAMEWORK = {
    # Tokens expire after AUTH_TOKEN_TTL_DAYS (see user/authentication.py)
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "user.authentication.ExpiringTokenAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 6,
    # Global + per-endpoint rate limits (user/throttles.py)
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "120/min",
        "user": "1000/min",
        "login": "10/min",
        "signup": "10/hour",
        "password_reset_request": "5/hour",
        "password_reset_confirm": "20/hour",
    },
}

AUTH_TOKEN_TTL_DAYS = int(os.environ.get("AUTH_TOKEN_TTL_DAYS", "30"))
MAX_UPLOAD_MB = int(os.environ.get("MAX_UPLOAD_MB", "5"))

SPECTACULAR_SETTINGS = {
    "TITLE": "Equb App API",
    "DESCRIPTION": "Equb App project api",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    # API docs only for platform admins (log into /admin/ first, or send a token)
    "SERVE_PERMISSIONS": ["user.permissions.IsAdminUser"],
    "SERVE_AUTHENTICATION": [
        "rest_framework.authentication.SessionAuthentication",
        "user.authentication.ExpiringTokenAuthentication",
    ],
}
# This is the key part to fix the template loading issue. It tells Django to look for templates in the "templates" directory at the project root.
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # ← make sure this line is correct
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

# CRONJOBS = [
#     ('24 15 * * *', 'order.tasks.generate_earning'),
# ]


CHAPA_SECRET_KEY = os.environ.get("CHAPA_SECRET_KEY", "")
# Chapa signs webhooks with the dashboard "secret hash"; defaults to the API key if unset.
CHAPA_WEBHOOK_SECRET = os.environ.get("CHAPA_WEBHOOK_SECRET") or CHAPA_SECRET_KEY
# CHAPA_BASE_URL removed — was unused (actual API host is hardcoded at call sites)


# --- SMS (password-reset codes) ---
# "console" prints the code to the server log (development).
# "afromessage" sends real SMS via AfroMessage; set the AFROMESSAGE_* values.
SMS_PROVIDER = os.environ.get("SMS_PROVIDER", "console")
AFROMESSAGE_TOKEN = os.environ.get("AFROMESSAGE_TOKEN", "")
AFROMESSAGE_IDENTIFIER_ID = os.environ.get("AFROMESSAGE_IDENTIFIER_ID", "")
AFROMESSAGE_SENDER_NAME = os.environ.get("AFROMESSAGE_SENDER_NAME", "")
PASSWORD_RESET_CODE_TTL_MINUTES = int(os.environ.get("PASSWORD_RESET_CODE_TTL_MINUTES", "10"))
