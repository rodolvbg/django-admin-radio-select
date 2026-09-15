from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Protocol

from django import forms
from django.core.exceptions import ImproperlyConfigured

from .formsets import make_radio_select_exclusive_formset
from .widgets import RadioCheckboxInput

if TYPE_CHECKING:
    from django.db.models import Model
    from django.forms import BaseInlineFormSet
    from django.http import HttpRequest

    class _InlineModelAdminLike(Protocol):
        """The slice of ``InlineModelAdmin`` this mixin's methods need
        from ``self``. A ``Protocol`` (structural) rather than the real
        ``InlineModelAdmin`` (nominal) so type checkers don't require
        ``RadioSelectMixin`` to actually inherit from it — it stays a
        real mixin at runtime, cooperating through ``super()`` with
        whatever ``InlineModelAdmin`` subclass it's combined with.
        """

        radio_select_exclusive_fields: Sequence[str]

        def get_radio_select_exclusive_fields(self, request: HttpRequest) -> Sequence[str]: ...

        def get_formset(
            self, request: HttpRequest, obj: Model | None = ..., **kwargs: Any
        ) -> type[BaseInlineFormSet]: ...


class RadioSelectMixin:
    """Mixin for ``TabularInline``/``StackedInline`` that renders the
    ``BooleanField``\\ s named in ``radio_select_exclusive_fields`` as
    radio buttons, synchronized client-side so selecting one clears the
    others in the same column — while every row keeps its own
    Django-generated field name, so the formset POST is completely
    unaffected.

    This is a plain mixin, not an ``InlineModelAdmin`` subclass: it
    relies on cooperative ``super()`` calls and is meant to sit before
    ``admin.TabularInline``/``admin.StackedInline`` in a subclass's
    bases. The ``self: _InlineModelAdminLike`` annotations below are for
    type checkers only and have no runtime effect; the ``# type: ignore``
    on the ``super()`` call silences mypy's ``safe-super`` check, which
    doesn't know the ``Protocol`` method it's resolving against is really
    backed by a concrete ``InlineModelAdmin`` at runtime.
    """

    radio_select_exclusive_fields: Sequence[str] = ()

    class Media:
        js = ("django_admin_radio_select/radio-select.js",)

    def get_radio_select_exclusive_fields(
        self: _InlineModelAdminLike, request: HttpRequest
    ) -> Sequence[str]:
        return tuple(self.radio_select_exclusive_fields)

    def get_formset(
        self: _InlineModelAdminLike,
        request: HttpRequest,
        obj: Model | None = None,
        **kwargs: Any,
    ) -> type[BaseInlineFormSet]:
        formset_class = super().get_formset(request, obj, **kwargs)  # type: ignore[safe-super]

        field_names = tuple(self.get_radio_select_exclusive_fields(request))
        if not field_names:
            return formset_class

        prefix = formset_class.get_default_prefix()
        _radioize_form_fields(formset_class.form, field_names, prefix)
        return make_radio_select_exclusive_formset(formset_class, field_names)


def _radioize_form_fields(
    form_class: type[forms.ModelForm], field_names: Sequence[str], prefix: str
) -> None:
    for field_name in field_names:
        field = form_class.base_fields.get(field_name)
        if not isinstance(field, forms.BooleanField):
            raise ImproperlyConfigured(
                f"{form_class.__name__}: radio_select_exclusive_fields references "
                f"'{field_name}', which must be a BooleanField on the form "
                f"(got {field.__class__.__name__ if field else 'nothing'})."
            )
        field.widget = RadioCheckboxInput(group=f"{prefix}::{field_name}", field_name=field_name)
        # A "must be checked" BooleanField can't represent the "this row
        # isn't the selected one" (False) state, which is a completely
        # valid, expected state for every row but one.
        field.required = False
