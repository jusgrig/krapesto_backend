import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# --- SECURITY ---
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'unsafe-production-key-123')
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'

# Update Allowed Hosts to include your domains
ALLOWED_HOSTS = ['57.128.249.100', 'krapesto.lt', 'www.krapesto.lt', 'localhost', '127.0.0.1']


# --- APPS ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', # Add this for WhiteNoise
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'core',
    'menu',
]

# --- MIDDLEWARE ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Place right after SecurityMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# --- AUTHENTICATION ---
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/user-menu/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# --- CORS ---
CORS_ALLOWED_ORIGINS = [
    "https://krapesto.lt",
    "https://www.krapesto.lt",
    "http://57.128.249.100:3000",
]
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
                'menu.context_processors.user_menu_language',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# --- DATABASE ---
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

# --- STATIC FILES (WhiteNoise Configuration) ---
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
# This is the magic line that fixes the "broken" layout
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
