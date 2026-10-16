"""django-admin-radio-select is now part of django-admin-rows.

This package only keeps the old imports working: use ``django_admin_rows``
(``from django_admin_rows import ExclusiveRadioFieldsMixin``) instead.
"""

import warnings

from django_admin_rows.radio_select import ExclusiveRadioFieldsMixin

warnings.warn(
    "django-admin-radio-select is now part of django-admin-rows: install "
    "django-admin-rows, import from django_admin_rows and put "
    "'django_admin_rows' in INSTALLED_APPS instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["ExclusiveRadioFieldsMixin"]

__version__ = "0.1.3"
