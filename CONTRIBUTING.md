# Contributing

## Setup

Python side is managed with [uv](https://docs.astral.sh/uv/). JS side with npm.

```bash
uv sync                              # creates .venv, installs the package + dev dependencies
uv run playwright install chromium   # once, for the e2e tests
npm install                          # installs vitest for the JS unit tests
```

## Project layout

- `src/django_admin_radio_select/` — the library (`mixins.py`, `widgets.py`, `formsets.py`, static JS).
- `example/` — a minimal Django project (`gallery` app: `Album` → `Image`) used both for manual local development and as the models/settings the test suite runs against.
- `tests/` — pytest tests (`test_package.py`, `test_widgets.py`, `test_mixins.py`, `test_formsets.py`, `test_admin_integration.py`, `test_changelist.py`, `test_e2e.py`) and vitest tests (`tests/js/`).

## Running the example project

```bash
uv run python example/manage.py migrate
uv run python example/manage.py createsuperuser
uv run python example/manage.py runserver
```

Visit `http://127.0.0.1:8000/admin/`. `Album` uses a `TabularInline` for its images and `radio_select_exclusive_fields` on its own changelist (`is_featured`, via `list_editable`); `Album (stacked inline demo)` (a proxy model) uses a `StackedInline` — so all three render paths can be exercised by hand.

If you change `example/gallery/models.py`, regenerate migrations:

```bash
uv run python example/manage.py makemigrations gallery
```

## Python tests (pytest + coverage)

```bash
uv run pytest
```

Coverage runs automatically (via `pytest-cov`, configured in `pyproject.toml`) and prints a report after the test run — only files with actual gaps are listed (`skip_covered`); a fully-covered file just counts toward the "N files skipped due to complete coverage" line. Tests run against `example.settings` with `--no-migrations` — tables are built straight from the models, so migrations and tests can't drift out of sync.

`tests/test_e2e.py` is included in that same `uv run pytest` run: real end-to-end tests via [`pytest-playwright`](https://playwright.dev/python/docs/test-runners), driving a real Chromium against a real Django server (`pytest-django`'s `live_server` fixture) — the JS module and the server-side validation, actually working together, not each mocked out for the other. They need `uv run playwright install chromium` once (see Setup above) and are slower than the rest of the suite; everything else here is unit/integration-level and doesn't touch a browser.

## JS unit tests (vitest)

```bash
npm run coverage
```

`src/django_admin_radio_select/static/django_admin_radio_select/radio-select.js` is a small, dependency-free script with no build step: `tests/js/radio-select.test.js` imports it directly for its side effect (registering the delegated `change` listener on `document`, exactly as a real page load would) and drives it with jsdom. `npm test` runs the suite without coverage; `npm run coverage` (used in CI) also runs it with coverage (`@vitest/coverage-v8`, configured in `vitest.config.js`) and prints a report after the test run.

## Lint, format, type-check

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src example
```

Or all of the above (plus the JS/TOML/misc checks) in one go via [pre-commit](https://pre-commit.com/):

```bash
uv run pre-commit install   # once, wires it into git commit
uv run pre-commit run --all-files
```

## Before opening a PR

```bash
uv run pytest
npm run coverage
uv run pre-commit run --all-files
```
