from django.apps import AppConfig
from django.conf import settings
from django.contrib.gis.geoip2 import HAS_GEOIP2
import logging

if "admin_auto_filters" not in settings.INSTALLED_APPS:
    settings.INSTALLED_APPS.append("admin_auto_filters")


class DjangoSessionsNgConfig(AppConfig):
    name = "django_user_sessions_ng"
    label = "django_user_sessions_ng"
    verbose_name = "Django User Sessions NG"
    models_module = "django_user_sessions_ng.models"

    def ready(self) -> None:
        if not HAS_GEOIP2:
            logging.warning("GeoIP2 is not available.")

        super().ready()
