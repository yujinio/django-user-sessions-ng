import logging

from django.contrib.gis.geoip2 import HAS_GEOIP2


def get_location_data(ip: str) -> dict | None:
    if not HAS_GEOIP2:
        return logging.error("GeoIP2 is not available.")

    from django.contrib.gis.geoip2 import GeoIP2

    try:
        g = GeoIP2()
    except Exception as e:  # FIXME: too broad exception clause
        return logging.error(str(e))

    try:
        return g.city(ip)
    except Exception:  # FIXME: too broad exception clause
        pass

    try:
        return g.country(ip)
    except Exception as e:  # FIXME: too broad exception clause
        return logging.error(str(e))


def get_human_readable_location(ip: str) -> str | None:
    if loc := get_location_data(ip):
        if loc.get("country_name"):
            if loc.get("city"):
                return f"{loc['city']}, {loc['country_name']}"
            return loc["country_name"]

    return None
