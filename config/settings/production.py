from .base import *
from decouple import config
from urllib.parse import urlparse

DEBUG = False


def _normalize_host(value):
    host = (value or "").strip()
    if not host:
        return ""
    if "://" in host:
        host = urlparse(host).netloc
    host = host.split("/")[0]
    host = host.split(":")[0]
    return host.strip()


_env_allowed_hosts = config("ALLOWED_HOSTS", default="")
_parsed_allowed_hosts = [_normalize_host(item) for item in _env_allowed_hosts.split(",")]
_parsed_allowed_hosts = [item for item in _parsed_allowed_hosts if item]

if not _parsed_allowed_hosts:
    _parsed_allowed_hosts = ["localhost", "127.0.0.1"]

_railway_public_domain = _normalize_host(config("RAILWAY_PUBLIC_DOMAIN", default=""))
if _railway_public_domain and _railway_public_domain not in _parsed_allowed_hosts:
    _parsed_allowed_hosts.append(_railway_public_domain)

_railway_static_url_host = _normalize_host(config("RAILWAY_STATIC_URL", default=""))
if _railway_static_url_host and _railway_static_url_host not in _parsed_allowed_hosts:
    _parsed_allowed_hosts.append(_railway_static_url_host)

if ".up.railway.app" not in _parsed_allowed_hosts:
    _parsed_allowed_hosts.append(".up.railway.app")

ALLOWED_HOSTS = _parsed_allowed_hosts

_csrf_trusted_origins = []
for host in ALLOWED_HOSTS:
    clean_host = (host or "").strip()
    if not clean_host:
        continue
    if clean_host.startswith("."):
        _csrf_trusted_origins.append("https://*{0}".format(clean_host))
    else:
        _csrf_trusted_origins.append("https://{0}".format(clean_host))
CSRF_TRUSTED_ORIGINS = _csrf_trusted_origins

# -------------------------------------------------------------------
# DATABASE
# Supports both SQLite (Railway volume) and PostgreSQL.
# Set DATABASE_URL in Railway environment variables:
#   SQLite:     sqlite:////mnt/data/db.sqlite3
#   PostgreSQL: postgresql://user:pass@host:5432/dbname
# -------------------------------------------------------------------
_database_url = config("DATABASE_URL", default="sqlite:////mnt/data/db.sqlite3")

if _database_url.startswith("sqlite"):
    import re
    _sqlite_path = re.sub(r"^sqlite:///", "", _database_url)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": _sqlite_path,
        }
    }
else:
    import dj_database_url
    DATABASES = {
        "default": dj_database_url.config(
            default=_database_url,
            conn_max_age=600,
        )
    }

# -------------------------------------------------------------------
# CACHE — uses local memory if no Redis configured
# -------------------------------------------------------------------
_redis_url = config("REDIS_URL", default="")
if _redis_url:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": _redis_url,
        }
    }
    CELERY_BROKER_URL = _redis_url
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }
    # Without Redis, Celery runs tasks synchronously
    CELERY_TASK_ALWAYS_EAGER = True

# Security
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Email
_email_backend = config("EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend")
EMAIL_BACKEND = _email_backend

if "sendgrid" in _email_backend or "anymail" in _email_backend:
    EMAIL_BACKEND = "anymail.backends.sendgrid.EmailBackend"
    ANYMAIL = {
        "SENDGRID_API_KEY": config("SENDGRID_API_KEY", default=""),
    }

_cors_origins = [item.strip() for item in config("CORS_ALLOWED_ORIGINS", default="").split(",")]
CORS_ALLOWED_ORIGINS = [item for item in _cors_origins if item]
CORS_ALLOW_CREDENTIALS = True
