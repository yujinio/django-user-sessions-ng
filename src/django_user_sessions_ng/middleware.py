import user_agents
from django.conf import settings
from django.contrib.sessions.middleware import (
    SessionMiddleware as DjangoSessionMiddleware,
)
from django.http import HttpRequest
from ipware import get_client_ip


class SessionMiddleware(DjangoSessionMiddleware):
    def process_request(self, request: HttpRequest) -> None:
        session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME, None)
        ip = get_client_ip(request)[0]
        user_agent = request.headers.get("User-Agent", None)
        device = str(user_agents.parse(user_agent)) if user_agent else None
        request.session = self.SessionStore(ip=ip, device=device, session_key=session_key)
