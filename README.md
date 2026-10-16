# django-admin-radio-select

[![Current version on PyPI](https://img.shields.io/pypi/v/django-admin-radio-select.svg)](https://pypi.org/project/django-admin-radio-select/)

> **This package is now part of
> [django-admin-rows](https://github.com/rodolvbg/django-admin-rows)**,
> with the same `ExclusiveRadioFieldsMixin` and new row-level extras for the
> Django admin. This last release only keeps the old imports working, with a
> `DeprecationWarning`; it gets no new features.

## Migrating

```bash
pip uninstall django-admin-radio-select
pip install django-admin-rows
```

| Before | After |
|---|---|
| `"django_admin_radio_select"` in `INSTALLED_APPS` | `"django_admin_rows"` |
| `from django_admin_radio_select import ExclusiveRadioFieldsMixin` | `from django_admin_rows import ExclusiveRadioFieldsMixin` |
| `django_admin_radio_select.widgets` / `.formsets` / `.mixins` | `django_admin_rows.radio_select.widgets` / `.formsets` / `.mixins` |

The options (`radio_select_exclusive_fields`,
`get_radio_select_exclusive_fields()`) and the behavior are the same: see
[django-admin-rows' README](https://github.com/rodolvbg/django-admin-rows#exclusive-radio-fields).

Until you migrate, this release installs django-admin-rows and keeps
working as it is, `INSTALLED_APPS` included.
