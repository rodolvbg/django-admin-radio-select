# django-admin-radio-select

[![Current version on PyPI](https://img.shields.io/pypi/v/django-admin-radio-select.svg)](https://pypi.org/project/django-admin-radio-select/)

> **This package is now part of
> [django-admin-tables](https://github.com/rodolvbg/django-admin-tables)**,
> with the same `ExclusiveRadioFieldsMixin` and other extras for the Django
> admin's tables (foreign key links, hideable and responsive columns, footer
> rows). This last release has **no code**: importing it raises an
> `ImportError` that says how to migrate. Pin `django-admin-radio-select<0.1.3`
> to keep using the old one until you do.

## Migrating

```bash
pip uninstall django-admin-radio-select
pip install django-admin-tables
```

| Before | After |
|---|---|
| `"django_admin_radio_select"` in `INSTALLED_APPS` | `"django_admin_tables"` |
| `from django_admin_radio_select import ExclusiveRadioFieldsMixin` | `from django_admin_tables import ExclusiveRadioFieldsMixin` (or `AdminTablesMixin`) |
| `django_admin_radio_select.widgets` / `.formsets` / `.mixins` | `django_admin_tables.radio_select.widgets` / `.formsets` / `.mixins` |

The options (`radio_select_exclusive_fields`,
`get_radio_select_exclusive_fields()`) and the behavior are the same: see
[django-admin-tables' README](https://github.com/rodolvbg/django-admin-tables#exclusive-radio-fields).
It requires Django 4.2+ and Python 3.10+.
