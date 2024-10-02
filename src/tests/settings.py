from pathlib import Path

DEBUG = True
ALLOWED_HOSTS = ("*",)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = "qwerty"
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "django_user_sessions_ng",
]
MIDDLEWARE = (
    "django_user_sessions_ng.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
)
ROOT_URLCONF = "tests.urls"
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "db.sqlite3"}}
SESSION_ENGINE = "django_user_sessions_ng.backends.cached_db"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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
STATIC_URL = "/static/"

GEOIP_PATH = BASE_DIR / "GeoLite"
