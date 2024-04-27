from django.contrib.sessions.backends.cached_db import SessionStore as DjangoSessionStore

from .db import SessionStore as DBSessionStore

KEY_PREFIX = "django_user_sessions_ng.cached_db"


class SessionStore(DBSessionStore, DjangoSessionStore):
    cache_key_prefix = KEY_PREFIX
