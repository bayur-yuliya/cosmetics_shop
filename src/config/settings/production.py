from urllib.parse import quote_plus

import dj_database_url

from .base import *

DEBUG = False

_hosts = os.getenv("ALLOWED_HOSTS", "")
ALLOWED_HOSTS = _hosts.split(",") if _hosts else []


db_user = os.getenv("DB_USER", "postgres")
db_password = quote_plus(os.getenv("DB_PASSWORD", ""))
db_host = os.getenv("DB_HOST", "db")
db_port = os.getenv("DB_PORT", "5432")
db_name = os.getenv("DB_NAME", "postgres")

db_url = os.getenv("DATABASE_URL")
if not db_url:
    db_user = os.getenv("DB_USER", "postgres")
    db_pass = quote_plus(os.getenv("DB_PASSWORD", ""))
    db_host = os.getenv("DB_HOST", "db")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "postgres")
    db_url = f"postgres://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

DATABASES = {
    "default": dj_database_url.parse(
        db_url,
        conn_max_age=600,
        conn_health_checks=True,
    )
}

R2_CUSTOM_DOMAIN = os.getenv("R2_CUSTOM_DOMAIN")

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "access_key": os.getenv("R2_ACCESS_KEY_ID"),
            "secret_key": os.getenv("R2_SECRET_ACCESS_KEY"),
            "bucket_name": os.getenv("R2_BUCKET_NAME"),
            "endpoint_url": f"https://{os.getenv('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com",
            "custom_domain": os.getenv("R2_CUSTOM_DOMAIN"),
            "location": "media",
            "region_name": "auto",
            "file_overwrite": False,
        },
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = os.getenv("MEDIA_URL", "")
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

STATIC_ROOT = BASE_DIR.parent / "staticfiles"

WHITENOISE_MANIFEST_STRICT = False

# Secure
# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

SITE_URL = os.getenv("SITE_URL", "")

AWS_QUERYSTRING_AUTH = False

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "")
