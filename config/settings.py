"""
Django settings for config project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import cloudinary

# ==================================================
# BASE DIR
# ==================================================
BASE_DIR = Path(__file__).resolve().parent.parent

# ==================================================
# LOAD ENV
# ==================================================
load_dotenv(BASE_DIR / ".env")

# ==================================================
# SECURITY
# ==================================================
SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-dev-key")

DEBUG = os.getenv("DEBUG", "").lower() == "true"

ALLOWED_HOSTS = [
    "doctor-appointment-gpam.onrender.com",
    ".onrender.com",
    "localhost",
    "127.0.0.1",
]

# ==================================================
# APPLICATIONS
# ==================================================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "drf_spectacular",

    # ✅ ORDER MATTERS (FIX)
    "cloudinary_storage",
    "cloudinary",

    # Local apps
    "apps.accounts",
    "apps.appointments",
    "apps.consultations",
]

# ==================================================
# MIDDLEWARE
# ==================================================
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

# ==================================================
# URLS / WSGI
# ==================================================
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

# ==================================================
# TEMPLATES
# ==================================================
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

# ==================================================
# DATABASE
# ==================================================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT", "5432"),
        "OPTIONS": {"sslmode": "require"},
    }
}

# ==================================================
# PASSWORD VALIDATION
# ==================================================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ==================================================
# INTERNATIONALIZATION
# ==================================================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ==================================================
# STATIC FILES (WHITENOISE)
# ==================================================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

if DEBUG:
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
else:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

# ==================================================
# MEDIA (LOCAL FALLBACK ONLY)
# ==================================================
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ==================================================
# DEFAULT PRIMARY KEY
# ==================================================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ==================================================
# REST FRAMEWORK
# ==================================================
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# ==================================================
# CLOUDINARY (FIXED)
# ==================================================
CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")

if CLOUDINARY_URL:
    cloudinary.config(
        cloudinary_url=CLOUDINARY_URL,
        secure=True,
    )

    DEFAULT_FILE_STORAGE = (
        "cloudinary_storage.storage.MediaCloudinaryStorage"
    )
else:
    DEFAULT_FILE_STORAGE = (
        "django.core.files.storage.FileSystemStorage"
    )
