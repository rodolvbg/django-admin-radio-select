from pathlib import Path

import django_admin_rows
from django.apps import AppConfig


class DjangoAdminRadioSelectConfig(AppConfig):
    name = "django_admin_radio_select"
    verbose_name = "Django Admin Radio Select"
    # The radios' JS now lives in django_admin_rows: serve its static files
    # from here, for projects that still list only this app.
    path = str(Path(django_admin_rows.__file__).parent)
