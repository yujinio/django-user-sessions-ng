import json

import pytest
import user_agents
from django.apps import apps
from django.contrib.auth import SESSION_KEY
from django.contrib.auth.models import User

from django_user_sessions_ng import SESSION_DEVICE_KEY, SESSION_IP_KEY

Session = apps.get_model("django_user_sessions_ng", "Session")
USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3"
DEVICE = str(user_agents.parse(USER_AGENT))


@pytest.mark.django_db
def test_unmodified_session(client, settings):
    client.get("/", HTTP_USER_AGENT=USER_AGENT)
    assert settings.SESSION_COOKIE_NAME not in client.cookies


@pytest.mark.django_db
@pytest.mark.parametrize("logged_in", (False, True))
def test_modify_session(client, settings, logged_in: bool):
    if logged_in:
        user = User.objects.create_superuser("user", "", "secret")
        client.force_login(user)

    read_session_response = client.get("/read-session/", HTTP_USER_AGENT=USER_AGENT)
    read_session_data = json.loads(read_session_response.content.decode("UTF-8"))
    print("read_session_response", read_session_data)

    modify_session_response = client.get("/modify-session/", HTTP_USER_AGENT=USER_AGENT)
    modify_session_data = json.loads(modify_session_response.content.decode("UTF-8"))
    print("modify_session_data", modify_session_data)

    new_read_session_response = client.get("/read-session/", HTTP_USER_AGENT=USER_AGENT)
    new_read_session_data = json.loads(new_read_session_response.content.decode("UTF-8"))

    assert read_session_data != modify_session_data

    if logged_in:
        assert new_read_session_data == modify_session_data
    else:
        assert new_read_session_data != modify_session_data

    assert "ping" not in read_session_data
    assert "ping" in modify_session_data
    assert "ping" in new_read_session_data
    assert SESSION_IP_KEY not in read_session_data

    if logged_in:
        assert SESSION_IP_KEY in modify_session_data
    else:
        assert SESSION_IP_KEY not in modify_session_data
    assert SESSION_IP_KEY in new_read_session_data
    assert SESSION_DEVICE_KEY not in read_session_data
    if logged_in:
        assert SESSION_DEVICE_KEY in modify_session_data
    else:
        assert SESSION_DEVICE_KEY not in modify_session_data
    assert SESSION_DEVICE_KEY in new_read_session_data

    assert modify_session_data["ping"] == "pong"
    assert new_read_session_data["ping"] == "pong"
    assert new_read_session_data[SESSION_IP_KEY] == "127.0.0.1"
    assert new_read_session_data[SESSION_DEVICE_KEY] == DEVICE

    if logged_in:
        assert SESSION_KEY in read_session_data
        assert SESSION_KEY in modify_session_data
        assert SESSION_KEY in new_read_session_data

        assert (
            read_session_data[SESSION_KEY]
            == modify_session_data[SESSION_KEY]
            # == new_read_session_data[SESSION_KEY]
            == str(user.id)
        )

    assert settings.SESSION_COOKIE_NAME in client.cookies
    session = Session.objects.get(pk=client.cookies[settings.SESSION_COOKIE_NAME].value)
    assert session.device == DEVICE
    assert session.ip == "127.0.0.1"
    if logged_in:
        assert session.user == user
    else:
        assert session.user is None
