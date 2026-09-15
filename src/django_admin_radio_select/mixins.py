from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Protocol, TypeVar

from django import forms
from django.core.exceptions import ImproperlyConfigured

from .formsets import make_radio_select_exclusive_formset
from .widgets import RadioCheckboxInput

if TYPE_CHECKING:
    from django.db.models import Model
    from django.forms.models import BaseInlineFormSet, BaseModelFormSet
    from django.http import HttpRequest

    class _InlineModelAdminLike(Protocol):
        """The slice of ``InlineModelAdmin`` ``get_formset`` needs from
        ``self``. A ``Protocol`` (structural) rather than the real
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

    class _ModelAdminLike(Protocol):
        """Same idea as ``_InlineModelAdminLike``, for the slice of
        ``ModelAdmin`` ``get_changelist_formset`` needs.
        """

        radio_select_exclusive_fields: Sequence[str]

        def get_radio_select_exclusive_fields(self, request: HttpRequest) -> Sequence[str]: ...

        def get_changelist_formset(
            self, request: HttpRequest, **kwargs: Any
        ) -> type[BaseModelFormSet]: ...


class RadioSelectMixin:
    """Mixin for ``ModelAdmin``, ``TabularInline``, or ``StackedInline``
    that renders the ``BooleanField``\\ s named in
    ``radio_select_exclusive_fields`` as radio buttons, synchronized
    client-side so selecting one clears the others in the same column —
    while every row keeps its own Django-generated field name, so the
    formset POST is completely unaffected.

    - On an inline, this applies to every row of that inline's formset.
    - On a ``ModelAdmin``, it applies to the changelist's
      ``list_editable`` formset — the field must be in both
      ``list_display`` and ``list_editable`` for Django to render it as
      an editable column at all; ``radio_select_exclusive_fields`` only
      controls how that column renders and is validated, same as inline.

    This is a plain mixin, not an ``InlineModelAdmin``/``ModelAdmin``
    subclass: it relies on cooperative ``super()`` calls and is meant to
    sit before ``admin.ModelAdmin``/``admin.TabularInline``/
    ``admin.StackedInline`` in a subclass's bases. The
    ``self: _InlineModelAdminLike`` / ``self: _ModelAdminLike``
    annotations below are for type checkers only and have no runtime
    effect; the ``# type: ignore`` on each ``super()`` call silences
    mypy's ``safe-super`` check, which doesn't know the ``Protocol``
    method it's resolving against is really backed by a concrete
    ``InlineModelAdmin``/``ModelAdmin`` at runtime.
    """

    radio_select_exclusive_fields: Sequence[str] = ()

    class Media:
        js = ("django_admin_radio_select/radio-select.js",)

    def get_radio_select_exclusive_fields(
        self: _InlineModelAdminLike | _ModelAdminLike, request: HttpRequest
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
        return _wrap_formset(formset_class, field_names)

    def get_changelist_formset(
        self: _ModelAdminLike, request: HttpRequest, **kwargs: Any
    ) -> type[BaseModelFormSet]:
        formset_class = super().get_changelist_formset(request, **kwargs)  # type: ignore[safe-super]
        field_names = tuple(self.get_radio_select_exclusive_fields(request))
        return _wrap_formset(formset_class, field_names)


_FormSetT = TypeVar("_FormSetT", bound="BaseModelFormSet")


def _wrap_formset(formset_class: type[_FormSetT], field_names: Sequence[str]) -> type[_FormSetT]:
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
