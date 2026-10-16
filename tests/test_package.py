"""The compatibility layer over django-admin-rows."""

import importlib

import pytest
from django.contrib.staticfiles import finders
from django_admin_rows import radio_select

import django_admin_radio_select


def test_importing_it_warns():
    with pytest.warns(DeprecationWarning, match="django-admin-rows"):
        importlib.reload(django_admin_radio_select)


def test_the_old_imports_are_django_admin_rows_objects():
    from django_admin_radio_select import ExclusiveRadioFieldsMixin
    from django_admin_radio_select.formsets import make_radio_select_exclusive_formset
    from django_admin_radio_select.mixins import ExclusiveRadioFieldsMixin as Mixin
    from django_admin_radio_select.widgets import RadioCheckboxInput, theme_classes

    assert ExclusiveRadioFieldsMixin is Mixin is radio_select.ExclusiveRadioFieldsMixin
    assert RadioCheckboxInput is radio_select.widgets.RadioCheckboxInput
    assert theme_classes is radio_select.widgets.theme_classes
    assert (
        make_radio_select_exclusive_formset
        is radio_select.formsets.make_radio_select_exclusive_formset
    )


def test_the_radios_js_is_found_with_only_this_app_installed(settings):
    assert "django_admin_rows" not in settings.INSTALLED_APPS
    assert finders.find("django_admin_rows/radio-select.js")
