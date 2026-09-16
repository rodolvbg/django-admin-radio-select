import django_admin_radio_select
from django_admin_radio_select import ExclusiveRadioFieldsMixin
from django_admin_radio_select.formsets import make_radio_select_exclusive_formset
from django_admin_radio_select.mixins import (
    ExclusiveRadioFieldsMixin as MixinFromModule,
)
from django_admin_radio_select.widgets import RadioCheckboxInput


def test_public_api_is_importable_from_top_level_package():
    assert ExclusiveRadioFieldsMixin is MixinFromModule


def test_package_exposes_a_version():
    assert isinstance(django_admin_radio_select.__version__, str)
    assert django_admin_radio_select.__version__


def test_internal_modules_are_importable():
    assert callable(make_radio_select_exclusive_formset)
    assert issubclass(RadioCheckboxInput, object)
