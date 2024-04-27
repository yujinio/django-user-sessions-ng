from django.contrib import admin
from django.http import HttpRequest, JsonResponse
from django.urls import path


def read_session(request: HttpRequest) -> JsonResponse:
    return JsonResponse(dict(request.session))


def modify_session(request: HttpRequest) -> JsonResponse:
    request.session["ping"] = "pong"
    return read_session(request)


urlpatterns = [
    path("read-session/", read_session),
    path("modify-session/", modify_session),
    path("admin/", admin.site.urls),
]
