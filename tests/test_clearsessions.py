from datetime import timedelta

import pytest
from django.apps import apps
from django.core.management import call_command
from django.utils import timezone

Session = apps.get_model("django_user_sessions_ng", "Session")


@pytest.mark.django_db
def test_can_call():
    Session.objects.create(
        session_key="s1",
        expire_date=timezone.now() + timedelta(hours=1),
        ip="127.0.0.1",
    )
    Session.objects.create(
        session_key="s2",
        expire_date=timezone.now() - timedelta(hours=1),
        ip="127.0.0.1",
    )
    assert Session.objects.count() == 2
    call_command("clearsessions")
    assert Session.objects.count() == 1
