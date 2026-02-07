"""
Django settings for config project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# =========================
# BASE DIRECTORY
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# LOAD .env FILE (MUST BE HERE)
# =========================
load_dotenv(dotenv_path=BASE_DIR / '.env')


# =========================
# SECURITY
# =========================
SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-dev-key")
DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS",
    "doctor-appointment-gpam.onrender.com"
).split(",")


# =========================
# APPLICATIONS
# INSTALLED_APPS = [
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',      # 🔥 REQUIRED
    'drf_yasg',

    'apps.accounts',
    'apps.appointments',
    'apps.consultations',
]


# =========================
# MIDDLEWARE
# =========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',  # 👈 REQUIRED FIRST

    'apps.accounts.middleware.RedirectAuthenticatedUserMiddleware',  # 👈 AFTER

    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]



# =========================
# URL CONFIG
# =========================
ROOT_URLCONF = 'config.urls'


# =========================
# TEMPLATES
# =========================
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


# =========================
# WSGI
# =========================
WSGI_APPLICATION = 'config.wsgi.application'


# =========================
# DATABASE (POSTGRESQL)
# =========================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

# =========================
# PASSWORD VALIDATION
# =========================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# =========================
# INTERNATIONALIZATION
# =========================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# =========================
# STATIC FILES
# =========================
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'


# =========================
# MEDIA FILES (FOR IMAGE UPLOAD)
# =========================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# =========================
# DEFAULT PRIMARY KEY
# =========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}
