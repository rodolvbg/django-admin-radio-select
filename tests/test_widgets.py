from django_admin_radio_select.widgets import RadioCheckboxInput


def test_renders_as_type_radio():
    widget = RadioCheckboxInput(group="images::is_primary", field_name="is_primary")

    assert widget.input_type == "radio"
    html = widget.render("is_primary", None)
    assert 'type="radio"' in html
    assert 'type="checkbox"' not in html


def test_attrs_carry_group_and_field_name():
    widget = RadioCheckboxInput(group="images::is_primary", field_name="is_primary")

    assert widget.attrs["data-radio-select-group"] == "images::is_primary"
    assert widget.attrs["data-radio-select-field"] == "is_primary"
    assert "radio-select-exclusive" in widget.attrs["class"]


def test_existing_class_attr_is_preserved():
    widget = RadioCheckboxInput(
        group="images::is_primary", field_name="is_primary", attrs={"class": "existing"}
    )

    assert widget.attrs["class"] == "existing radio-select-exclusive"


def test_checked_state_reflects_current_value():
    widget = RadioCheckboxInput(group="images::is_primary", field_name="is_primary")

    assert "checked" in widget.render("is_primary", True)
    assert "checked" not in widget.render("is_primary", False)


def test_value_from_datadict_matches_checkbox_semantics():
    # Present in the POST data => True; absent => False. Exactly what a
    # BooleanField's own default widget (CheckboxInput) does, and what
    # makes this drop-in safe for the field's clean()/validate().
    widget = RadioCheckboxInput(group="images::is_primary", field_name="is_primary")

    assert widget.value_from_datadict({}, {}, "is_primary") is False
    assert widget.value_from_datadict({"is_primary": "on"}, {}, "is_primary") is True
