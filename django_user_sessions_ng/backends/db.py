from typing import Type

from django.apps import apps
from django.contrib import auth
from django.contrib.sessions.backends.db import SessionStore as DjangoSessionStore
from django.utils import timezone

from django_user_sessions_ng import SESSION_DEVICE_KEY, SESSION_IP_KEY

Session = apps.get_model("django_user_sessions_ng", "Session")


class SessionStore(DjangoSessionStore):
    ip: str | None
    device: str | None

    def __init__(self, session_key: str | None = None, ip: str | None = None, device: str | None = None):
        super().__init__(session_key)
        self.ip = ip
        self.device = device[:255] if device else None

    @classmethod
    def get_model_class(cls) -> Type[Session]:  # type: ignore
        return Session

    @property
    def key_salt(self) -> str:
        return "django_user_sessions_ng." + self.__class__.__qualname__

    @property
    def user_id(self) -> str | None:
        return self.get(auth.SESSION_KEY)

    def create_model_instance(self, data: dict) -> Session:  # type: ignore
        now = timezone.now()
        return self.model(
            session_key=self._get_or_create_session_key(),
            session_data=self.encode(data),
            expire_date=self.get_expiry_date(),
            user_id=self.user_id,
            ip=self.ip,
            device=self.device,
            created_at=now,
            updated_at=now,
        )

    def load(self) -> dict:
        data: dict = super().load()
        device = data.get(SESSION_DEVICE_KEY)
        ip = data.get(SESSION_IP_KEY)
        if device != self.device or ip != self.ip:
            self.modified = True
        return data

    def save(self, must_create: bool = False) -> Session:  # type: ignore
        if self.get(SESSION_DEVICE_KEY) != self.device:
            self[SESSION_DEVICE_KEY] = self.device
        if self.get(SESSION_IP_KEY) != self.ip:
            self[SESSION_IP_KEY] = self.ip

        return super().save(must_create)
