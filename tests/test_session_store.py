from datetime import timedelta

import pytest
from django.apps import apps
from django.conf import settings
from django.contrib import auth
from django.contrib.sessions.backends.base import CreateError
from django.utils.timezone import now

from django_user_sessions_ng import SESSION_DEVICE_KEY, SESSION_IP_KEY
from django_user_sessions_ng.backends import SessionBaseChild

Session = apps.get_model("django_user_sessions_ng", "Session")


@pytest.fixture
def session_store(session_store_class) -> SessionBaseChild:
    return session_store_class(ip="127.0.0.1", device="Test Device")


def test_untouched_session_store(session_store):
    assert not session_store.modified
    assert not session_store.accessed
    assert session_store.is_empty()


def test_session_store(session_store):
    session_store["ping"] = "pong"
    assert session_store.accessed
    assert session_store.modified
    assert not session_store.is_empty()
    assert "ping" in session_store
    assert session_store.pop("ping") == "pong"
    assert "ping" not in session_store
    assert session_store.get("ping") is None


def test_auth_session_key(session_store):
    assert auth.SESSION_KEY not in session_store
    assert not session_store.modified
    assert session_store.accessed

    session_store.get(auth.SESSION_KEY)
    assert not session_store.modified

    session_store[auth.SESSION_KEY] = 1
    assert session_store.modified


@pytest.mark.django_db
def test_save(session_store, django_user_model):
    django_user_model.objects.create_user(username="test_user")

    session_store[auth.SESSION_KEY] = 1
    session_store.save()

    session = Session.objects.get(pk=session_store.session_key)
    assert session.device == "Test Device"
    assert session.ip == "127.0.0.1"
    assert session.user_id == 1
    assert now() - timedelta(seconds=5) <= session.updated_at <= now()


@pytest.mark.django_db
def test_load_unmodified(session_store_class, session_store, django_user_model):
    django_user_model.objects.create_user(username="test_user")

    session_store[auth.SESSION_KEY] = 1
    session_store.save()
    session_store2 = session_store_class(session_key=session_store.session_key, device="Test Device", ip="127.0.0.1")
    session_store2.load()
    assert session_store2.get(SESSION_DEVICE_KEY) == "Test Device"
    assert session_store2.get(SESSION_IP_KEY) == "127.0.0.1"
    assert session_store2.get(auth.SESSION_KEY) == 1
    assert session_store2.modified is False


@pytest.mark.django_db
def test_load_modified(session_store_class, session_store, django_user_model):
    django_user_model.objects.create_user(username="test_user")

    session_store[auth.SESSION_KEY] = 1
    session_store.save()

    session_store2 = session_store_class(
        session_key=session_store.session_key, device="Test Device Changed", ip="8.8.8.8"
    )
    session_store2.load()

    assert session_store2.get(SESSION_DEVICE_KEY) == "Test Device"
    assert session_store2.get(SESSION_IP_KEY) == "127.0.0.1"
    assert session_store2.get(auth.SESSION_KEY) == 1
    assert session_store2.modified is True

    session_store2.save()

    assert session_store2.get(SESSION_DEVICE_KEY) == "Test Device Changed"
    assert session_store2.get(SESSION_IP_KEY) == "8.8.8.8"


@pytest.mark.django_db
def test_duplicate_create(session_store_class):
    s1 = session_store_class(session_key="DUPLICATE", device="Test Device", ip="127.0.0.1")
    s1.create()
    s2 = session_store_class(session_key="DUPLICATE", device="Test Device", ip="127.0.0.1")
    s2.create()
    assert s1.session_key != s2.session_key

    s3 = session_store_class(session_key=s1.session_key, device="Test Device", ip="127.0.0.1")
    with pytest.raises(CreateError):
        s3.save(must_create=True)


@pytest.mark.django_db
def test_delete(session_store):
    # session_store persisted, should just return
    session_store.delete()

    # create, then delete
    session_store.create()
    session_key = session_store.session_key
    session_store.delete()

    # non-existing sessions, should not raise
    session_store.delete()
    session_store.delete(session_key)


@pytest.mark.django_db
def test_clear(session_store):
    # clearing the session should clear all non-browser information
    session_store[auth.SESSION_KEY] = 1
    session_store.clear()
    session_store.save()

    session = Session.objects.get(pk=session_store.session_key)
    assert session.user_id is None


def test_import(session_store_class):
    if settings.SESSION_ENGINE.endswith(".cached_db"):

        from django_user_sessions_ng.backends.cached_db import SessionStore as CachedDBBackend

        assert issubclass(session_store_class, CachedDBBackend)
    elif settings.SESSION_ENGINE.endswith(".db"):
        from django_user_sessions_ng.backends.db import SessionStore as DBBackend

        assert issubclass(session_store_class, DBBackend)
    else:
        assert False, "Unrecognised Session Engine"
