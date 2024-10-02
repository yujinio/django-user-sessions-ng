from importlib import import_module

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sessions.base_session import AbstractBaseSession, BaseSessionManager
from django.core.cache import caches
from django.db import models

from django_user_sessions_ng.backends import SessionBaseChild

from .geoip import get_human_readable_location, get_location_data

User = get_user_model()


class SessionQuerySet(models.QuerySet):
    def delete(self) -> tuple[int, dict[str, int]]:
        SessionStore = Session.get_session_store_class()
        if prefix := getattr(SessionStore, "cache_key_prefix", None):
            caches[settings.SESSION_CACHE_ALIAS].delete_many((f"{prefix}{session.session_key}" for session in self))
        return super().delete()


class SessionManager(BaseSessionManager.from_queryset(SessionQuerySet)):
    use_in_migrations = True


class Session(AbstractBaseSession):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions", db_index=True, null=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    device = models.CharField(max_length=255, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SessionManager()

    @classmethod
    def get_session_store_class(cls) -> SessionBaseChild:
        return import_module(settings.SESSION_ENGINE).SessionStore

    @property
    def location_data(self) -> dict | None:
        return get_location_data(self.ip)

    @property
    def location(self) -> str | None:
        return get_human_readable_location(self.ip)

    def delete(self, using=None, keep_parents: bool = False) -> tuple[int, dict[str, int]]:
        SessionStore = self.get_session_store_class()
        if prefix := getattr(SessionStore, "cache_key_prefix", None):
            caches[settings.SESSION_CACHE_ALIAS].delete(f"{prefix}{self.session_key}")
        return super().delete(using=using, keep_parents=keep_parents)

    class Meta(AbstractBaseSession.Meta):
        db_table = "django_user_sessions_ng_user_sessions"
        verbose_name = "session"
        verbose_name_plural = "sessions"
        ordering = ("-created_at",)
