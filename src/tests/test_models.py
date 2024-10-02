import random
import string

import pytest
from django.contrib import auth

from django_user_sessions_ng import SESSION_DEVICE_KEY, SESSION_IP_KEY
from django_user_sessions_ng.models import Session


def get_random_string(length: int) -> str:
    return "".join(random.choices(string.ascii_letters, k=length))


@pytest.mark.django_db
def test_get_decoded(session_store_class, django_user_model):
    django_user_model.objects.create_user(username="test_user")

    store = session_store_class(device="Test Device", ip="127.0.0.1")
    store[auth.SESSION_KEY] = 1
    store["foo"] = "bar"
    store.save()

    session = Session.objects.get(pk=store.session_key)
    assert session.get_decoded() == {
        "foo": "bar",
        auth.SESSION_KEY: 1,
        SESSION_IP_KEY: "127.0.0.1",
        SESSION_DEVICE_KEY: "Test Device",
    }


@pytest.mark.django_db
def test_very_long_device(session_store_class):
    device = get_random_string(256)
    store = session_store_class(device=device, ip="127.0.0.1")
    store.save()

    session = Session.objects.get(pk=store.session_key)
    assert session.device == device[:255]


@pytest.mark.django_db
def test_delete(session_store_class):
    """
    Session.delete should delete session from both DB and cache
    """
    store = session_store_class(device="Test Device", ip="127.0.0.1")
    store.create()
    session_key = store.session_key

    session = Session.objects.get(pk=session_key)
    session.delete()

    assert not store.exists(session_key)


@pytest.mark.django_db
def test_bulk_delete_from_both_cache_and_db(session_store_class):
    s1 = session_store_class(device="Test Device 1", ip="127.0.0.1")
    s1.create()
    s2 = session_store_class(device="Test Device 1", ip="127.0.0.1")
    s2.create()
    s3 = session_store_class(device="Test Device 2", ip="127.0.0.1")
    s3.create()
    assert s1.exists(s1.session_key)
    assert s2.exists(s2.session_key)
    assert s3.exists(s3.session_key)
    Session.objects.filter(device="Test Device 1").delete()
    assert not s1.exists(s1.session_key)
    assert not s2.exists(s2.session_key)
    assert s3.exists(s3.session_key)
