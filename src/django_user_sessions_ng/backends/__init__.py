from typing import TypeVar

from django.contrib.sessions.backends.base import SessionBase

SessionBaseChild = TypeVar("SessionBaseChild", bound="SessionBase")
