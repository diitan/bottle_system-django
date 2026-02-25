#Khi DEBUG=False thì chạy trước câu lệnh này:   python manage.py collectstatic
import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# ======================================
# BASE DIR
# ======================================
BASE_DIR = Path(__file__).resolve().parent.parent

# ======================================
# LOAD .ENV (LOCAL ONLY)
# ======================================
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path)

# ======================================
# CORE SETTINGS
# ======================================
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

DEBUG = os.getenv("DEBUG", "0") == "1"
#DEBUG = True

# ======================================
# ALLOWED HOSTS
# ======================================
if DEBUG:
    ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
else:
    ALLOWED_HOSTS = (
        os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost")
        .split(",")
    )

    # đảm bảo Render domain luôn hợp lệ
    ALLOWED_HOSTS.append(".onrender.com")

# ======================================
# APPLICATIONS
# ======================================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",

    "core",
    "accounts",
    "orders",
]

# ======================================
# MIDDLEWARE
# ======================================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
]

# WhiteNoise chỉ dùng production
if not DEBUG:
    MIDDLEWARE.append("whitenoise.middleware.WhiteNoiseMiddleware")

MIDDLEWARE += [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "bottle_web.urls"

# ======================================
# TEMPLATES
# ======================================
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

WSGI_APPLICATION = "bottle_web.wsgi.application"

# ======================================
# DATABASE
# ======================================
DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
        conn_max_age=600,
    )
}

# ======================================
# STATIC FILES
# ======================================
STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"

if DEBUG:
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
else:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ======================================
# CSRF (important for Render)
# ======================================
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]

if DEBUG and not CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS = [
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ]

# ======================================
# LOGIN SETTINGS
# ======================================
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# ======================================
# SECURITY (Production only)
# ======================================
#if not DEBUG:
#    SECURE_SSL_REDIRECT = True
#    SESSION_COOKIE_SECURE = True
#    CSRF_COOKIE_SECURE = True
#else:
#    SECURE_SSL_REDIRECT = False
#    SESSION_COOKIE_SECURE = False
#    CSRF_COOKIE_SECURE = False