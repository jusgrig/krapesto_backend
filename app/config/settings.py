"""
Django settings for config project.
Production-ready for Docker + PostgreSQL
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ------------------------------------------------------------------------------
# SECURITY
# ------------------------------------------------------------------------------

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'fallback-key')

# DEBUG: Accept common truthy values ('1', 'true', 'True', 'yes', 'Yes')
DEBUG_VALUE = os.environ.get('DJANGO_DEBUG', 'False').lower()
DEBUG = DEBUG_VALUE in ('1', 'true', 'yes', 'on')
ALLOWED_HOSTS = [
    "57.128.249.100",
    "localhost",
    "127.0.0.1",
]


# ------------------------------------------------------------------------------
# APPLICATION DEFINITION
# ------------------------------------------------------------------------------

INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Local apps
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"


# ------------------------------------------------------------------------------
# TEMPLATES
# ------------------------------------------------------------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# ------------------------------------------------------------------------------
# WSGI
# ------------------------------------------------------------------------------

WSGI_APPLICATION = "config.wsgi.application"


# ------------------------------------------------------------------------------
# DATABASE (PostgreSQL)
# ------------------------------------------------------------------------------

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'krapesto'),
        'USER': os.environ.get('DB_USER', 'krapesto'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'krapesto0000'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# ------------------------------------------------------------------------------
# PASSWORD VALIDATION
# ------------------------------------------------------------------------------

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


# ------------------------------------------------------------------------------
# INTERNATIONALIZATION
# ------------------------------------------------------------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Vilnius"
USE_I18N = True
USE_TZ = True


# ------------------------------------------------------------------------------
# STATIC FILES
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# ------------------------------------------------------------------------------
# DEFAULT PRIMARY KEY
# ------------------------------------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
CSRF_TRUSTED_ORIGINS = [
    "http://57.128.249.100:8000",
]
