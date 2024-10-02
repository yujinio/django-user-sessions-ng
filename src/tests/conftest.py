import pytest
from django.apps import apps
from django.conf import settings

SESSION_ENGINES = (
    "django_user_sessions_ng.backends.db",
    "django_user_sessions_ng.backends.cached_db",
)


@pytest.fixture
def session_class():
    yield apps.get_model("django_user_sessions_ng", "Session")


@pytest.fixture(autouse=True, params=SESSION_ENGINES)
def session_store_class(request, session_class):
    settings.SESSION_ENGINE = request.param
    return session_class.get_session_store_class()
