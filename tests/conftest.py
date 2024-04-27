import pytest
from django.apps import apps
from django.conf import settings

Session = apps.get_model("django_user_sessions_ng", "Session")
SESSION_ENGINES = ("django_user_sessions_ng.backends.db", "django_user_sessions_ng.backends.cached_db")


@pytest.fixture(autouse=True, params=SESSION_ENGINES)
def session_store_class(request):
    settings.SESSION_ENGINE = request.param
    return Session.get_session_store_class()
