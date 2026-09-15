# django-admin-radio-select

Synchronize BooleanFields across Django Admin inline rows as mutually exclusive radio button groups.

## Problem

An inline `BooleanField` column renders as independent checkboxes:

```text
Image A    [ ]
Image B    [x]
Image C    [ ]
```

Nothing stops you from checking more than one — but often only one row should ever be true (the primary image, the default address, the featured item). This package renders that column as radio buttons instead:

```text
Image A    ( )
Image B    (•)
Image C    ( )
```

Selecting one clears the others, enforced with a small vanilla JS module. Every row still POSTs under its own normal Django-generated field name (e.g. `images-0-is_primary`, `images-1-is_primary`) — nothing here relies on giving different forms the same HTML `name`. A formset-level check on the server also rejects a handcrafted POST that tries to set more than one row true, so the guarantee doesn't depend on JavaScript running at all.

## Install

```bash
uv add django-admin-radio-select
# or
pip install django-admin-radio-select
```

Add the app so its static JS gets collected:

```python
INSTALLED_APPS = [
    ...,
    "django_admin_radio_select",
]
```

## Usage

```python
from django.contrib import admin
from django_admin_radio_select import RadioSelectMixin

from .models import Album, Image


class ImageInline(RadioSelectMixin, admin.TabularInline):
    model = Image
    radio_select_exclusive_fields = ("is_primary",)


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    inlines = [ImageInline]
```

Works the same way with `StackedInline`:

```python
class ImageInline(RadioSelectMixin, admin.StackedInline):
    model = Image
    radio_select_exclusive_fields = ("is_primary",)
```

Multiple fields are independent groups:

```python
class ImageInline(RadioSelectMixin, admin.TabularInline):
    model = Image
    radio_select_exclusive_fields = ("is_primary", "is_featured")
```

Compute the field list per request instead of (or in addition to) the class attribute:

```python
class ImageInline(RadioSelectMixin, admin.TabularInline):
    model = Image

    def get_radio_select_exclusive_fields(self, request):
        return ("is_primary",) if request.user.is_superuser else ()
```

Each configured name must be a `BooleanField` present on the inline's form; anything else raises `ImproperlyConfigured` when the admin builds the formset (a `python manage.py check`-time-ish failure, not a silent no-op).

## Supported versions

Python 3.10–3.13, Django 4.2–5.2. Currently supports `TabularInline` and `StackedInline`; `ModelAdmin` changelist support may follow later without changing this API.

## Development

Managed with [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

Run the example project:

```bash
uv run python example/manage.py migrate
uv run python example/manage.py createsuperuser
uv run python example/manage.py runserver
```

It's a minimal Album → Image gallery (`example/gallery`) with both a `TabularInline` and a `StackedInline` registration, so both can be exercised by hand at `/admin/`.

Run the tests:

```bash
uv run pytest
uv run coverage run -m pytest && uv run coverage report
```

Lint, format, and type-check:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src example
```
