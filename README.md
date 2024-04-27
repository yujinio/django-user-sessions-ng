# django-user-sessions-ng

`django-user-sessions-ng` is a Django package which allows users to have multiple sessions and provides session management through the Django admin interface.

This project is originally inspired by (and based on) the following projects:
1. [django-user-sessions](https://github.com/jazzband/django-user-sessions)
2. [django-qsessions](https://github.com/QueraTeam/django-qsessions)

The changes made in this repo, however, are very minimal, and the package itself is more like an adaptation for personal use.

## Features
1. Multiple sessions per user.
2. Session management through the Django admin interface.
3. Cached session data for faster access.
4. Device information for each session.
5. IP address for each session.
6. (Optional) Location information for each session.

## Installation

1. Install the package using your favorite package manager, for example pip:
    ```bash
    pip install django-user-sessions-ng
    ```

2. Add `django_user_sessions_ng` to your INSTALLED_APPS setting like this::
    ```python
    INSTALLED_APPS = [
        ...,
        "django_user_sessions_ng",
    ]
    ```

3. Add `django_user_sessions_ng.middleware.SessionMiddleware` to your MIDDLEWARE setting like this:
    ```python
    MIDDLEWARE = [
        ...,
        "django_user_sessions_ng.middleware.SessionMiddleware",
    ]
    ```

4. Set `SESSION_ENGINE` to `django_user_sessions_ng.backends.db` or `django_user_sessions_ng.backends.cached_db` depending on your preferences and whether you need cached db in your Django settings file:
    ```python
    SESSION_ENGINE = "django_user_sessions_ng.backends.db"
    ```
    or
    ```python
    SESSION_ENGINE = "django_user_sessions_ng.backends.cached_db"
    ```

5. Run `python manage.py migrate` to create the necessary models.

6. (Optional) In order to enable the location information for each session, you will need to install the package called `geoip2` and download the GeoLite2 database from [MaxMind](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data) or using the built-in `python manage.py download_geoip_db -k MAXMIND_LICENSE_KEY` command (you can get the `MAXMIND_LICENSE_KEY` by registering [at their website](https://www.maxmind.com/en/geolite2/signup) and registering a new license key) and set the `GEOIP_PATH` setting in your Django settings file to the path of the database file or directory containing multiple databases.

    For example:
    ```python
    GEOIP_PATH = "/path/to/GeoLite2"
    ```
    or
    ```python
    GEOIP_PATH = "/path/to/GeoLite2/GeoLite2-City.mmdb"
    ```


## Notes
1. Since this package replaces the functionality of the default Django session application (django.contrib.sessions), it is recommended to remove the `django.contrib.sessions` from the `INSTALLED_APPS` setting as well as `django.contrib.sessions.middleware.SessionMiddleware` from the `MIDDLEWARE` setting.
2. The package provides a management command `clearsessions` (simply imports the one from the original `django.contrib.sessions` package) which can be used to clear expired sessions. This command can be run using the following command:
    ```bash
    python manage.py django_user_sessions_ng clearsessions
    ```
3. If for some reason the MaxMind base url for download changes, and the package doesn't get updated in time, there's an optional argument `-u` or `--maxmind-geoip-download-base-url` for the `download_geoip_db` command which can be used to specify the base url for downloading the database files.

    For example:
    ```bash
    python manage.py download_geoip_db -k MAXMIND_LICENSE_KEY -u "https://download.maxmind.com/app/geoip_download"
    ```

## Credits
1. Thanks to [JazzBand](https://github.com/jazzband) for their original [django-user-sessions](https://github.com/jazzband/django-user-sessions) implementation.
2. Thanks to [QueraTeam](https://github.com/QueraTeam) for their original [django-qsessions](https://github.com/QueraTeam/django-qsessions), particularly for their tests and `cached_db` implementation.

## License
MIT
