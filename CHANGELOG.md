# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/0.1.1/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

- Compatibility matrix via tox (`[tool.tox]` in `pyproject.toml`, using
  [tox-uv](https://github.com/tox-dev/tox-uv)): tests every Django series
  in `classifiers` (4.2 through 5.2) against its oldest and newest
  supported Python, within this package's own floor. `uv run tox run`
  locally, a separate `compat-matrix.yml` CI workflow.
- `.github/workflows/pre-commit.yml`.

### Changed

- Build backend: `setuptools` → `hatchling` (confirmed via `uv build` +
  wheel inspection that `py.typed` and the static JS asset are still
  included by default under src-layout).
- `[tool.ruff] line-length` 100 → 88, to match the sibling `django-*`
  packages.
- `tests/test_e2e.py` moved to `tests/e2e/test_e2e.py` — browser
  end-to-end tests now live in their own subdirectory instead of mixed in
  with the rest of `tests/`.
- npm scripts split into `test` (no coverage), `test:watch`, and
  `coverage` (used by CI) — previously `test` always ran with coverage.

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
