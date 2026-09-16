# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/0.1.1/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [0.1.0] - 2026-09-16

### Added

- `ExclusiveRadioFieldsMixin` for `ModelAdmin`: renders `BooleanField` columns
  named in `radio_select_exclusive_fields` as mutually exclusive radio
  buttons, both on `TabularInline`/`StackedInline` formsets and on the
  changelist via `list_editable`. Selecting one row's radio clears the
  others in the same group.
- A formset-level server-side check that rejects a handcrafted POST setting
  more than one row true in the same exclusive group, so the guarantee
  holds even without JavaScript.
- `_get_effective_radio_select_exclusive_fields` to filter out readonly
  fields before radio-izing, so read-only `BooleanField`s are left as
  plain checkboxes/labels instead of being wrapped in a radio group.
- A small dependency-free JS module
  (`static/django_admin_radio_select/radio-select.js`) that synchronizes
  radio button state across dynamically added inline rows (Django admin's
  "Add another" formset rows), via a delegated `change` listener on
  `document`.
- `AppConfig` so the package works as a real Django app, letting
  `django.contrib.staticfiles` discover and serve its JS.
- `py.typed` marker for static type checking support.
- Full pytest suite (unit/integration tests for the mixin, widgets, and
  formsets, plus `pytest-playwright` end-to-end tests against a real
  Chromium browser and `pytest-django`'s `live_server`) and a vitest suite
  for the JS module.
