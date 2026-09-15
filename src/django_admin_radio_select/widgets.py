from __future__ import annotations

from typing import Any

from django.forms.widgets import CheckboxInput


class RadioCheckboxInput(CheckboxInput):
    """A :class:`~django.forms.CheckboxInput` rendered with
    ``type="radio"`` instead of ``type="checkbox"``.

    ``CheckboxInput`` already POSTs exactly the way a radio-per-row needs
    to: present in the data means checked, absent means unchecked/False.
    Only ``input_type`` changes here, which is all Django's widget
    templates key off of for the rendered ``type`` attribute — so a
    ``BooleanField`` using this widget round-trips through a normal
    Django form/formset completely unchanged; only the rendered control
    (and therefore its default browser styling and grouping semantics)
    is different.
    """

    input_type = "radio"

    def __init__(self, group: str, field_name: str, attrs: dict[str, Any] | None = None) -> None:
        attrs = dict(attrs or {})
        attrs["class"] = f"{attrs.get('class', '')} radio-select-exclusive".strip()
        attrs["data-radio-select-group"] = group
        attrs["data-radio-select-field"] = field_name
        super().__init__(attrs=attrs)
