import pytest
from django import forms
from django.contrib import admin as djadmin
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ImproperlyConfigured
from django.test import RequestFactory
from gallery.admin import ImageStackedInline, ImageTabularInline
from gallery.models import Album, Image

from django_admin_radio_select import ExclusiveRadioFieldsMixin
from django_admin_radio_select.widgets import RadioCheckboxInput

pytestmark = pytest.mark.django_db


@pytest.fixture
def request_(rf: RequestFactory):
    request = rf.get("/admin/")
    request.user = AnonymousUser()
    return request


@pytest.fixture
def site():
    return djadmin.AdminSite()


@pytest.fixture
def album():
    album = Album.objects.create(title="Holiday")
    Image.objects.create(album=album, title="A", is_primary=True)
    Image.objects.create(album=album, title="B", is_primary=False)
    Image.objects.create(album=album, title="C", is_primary=False)
    return album


@pytest.mark.parametrize("inline_class", [ImageTabularInline, ImageStackedInline])
def test_boolean_fields_become_radio_inputs(request_, site, inline_class):
    inline = inline_class(Album, site)
    formset_class = inline.get_formset(request_)

    for field_name in ("is_primary", "is_featured"):
        field = formset_class.form.base_fields[field_name]
        assert isinstance(field.widget, RadioCheckboxInput)
        assert field.required is False


def test_initial_selected_state_renders_checked_on_the_right_row(request_, site, album):
    inline = ImageTabularInline(Album, site)
    formset_class = inline.get_formset(request_)
    formset = formset_class(instance=album)
    html = str(formset)

    rows = {form.instance.title: form for form in formset.forms}
    assert "checked" in str(rows["A"]["is_primary"])
    assert "checked" not in str(rows["B"]["is_primary"])
    assert "checked" not in str(rows["C"]["is_primary"])
    assert html  # sanity: rendered without error


def test_rows_keep_independent_names_for_the_formset_post(request_, site, album):
    inline = ImageTabularInline(Album, site)
    formset_class = inline.get_formset(request_)
    formset = formset_class(instance=album)
    html = str(formset)

    assert 'name="images-0-is_primary"' in html
    assert 'name="images-1-is_primary"' in html
    assert 'name="images-0-is_featured"' in html


def test_multiple_configured_fields_get_independent_group_keys(request_, site):
    inline = ImageTabularInline(Album, site)
    formset_class = inline.get_formset(request_)

    base_fields = formset_class.form.base_fields
    primary_group = base_fields["is_primary"].widget.attrs["data-radio-select-group"]
    featured_group = base_fields["is_featured"].widget.attrs["data-radio-select-group"]

    assert primary_group != featured_group
    assert primary_group.endswith("::is_primary")
    assert featured_group.endswith("::is_featured")


def test_group_key_is_derived_from_the_formset_prefix(request_, site):
    # The group key a row's radio carries is exactly "<formset
    # prefix>::<field name>" — not the row index, and not anything tied
    # to a specific InlineModelAdmin instance. Two different inlines for
    # the same relation (e.g. a TabularInline and a StackedInline
    # version of the same FK, as in the example project) therefore only
    # share a group if they'd also share a formset prefix — which is
    # exactly when they're interchangeable renderings of the same rows.
    formset_class = ImageTabularInline(Album, site).get_formset(request_)
    group = formset_class.form.base_fields["is_primary"].widget.attrs["data-radio-select-group"]

    assert group == f"{formset_class.get_default_prefix()}::is_primary"


def test_empty_form_template_shares_the_group_key_with_real_rows(request_, site, album):
    # This is what Django admin's "Add another" JS clones client-side:
    # since the group key only depends on the formset prefix + field
    # name (not the row index), a dynamically added row is already in
    # the right group with no extra JS-side computation.
    inline = ImageTabularInline(Album, site)
    formset_class = inline.get_formset(request_)
    formset = formset_class(instance=album)

    bound_group = formset.forms[0].fields["is_primary"].widget.attrs["data-radio-select-group"]
    empty_group = formset.empty_form.fields["is_primary"].widget.attrs["data-radio-select-group"]

    assert bound_group == empty_group


def test_unconfigured_field_is_left_alone(request_, site):
    class PlainInline(ExclusiveRadioFieldsMixin, djadmin.TabularInline):
        model = Image
        radio_select_exclusive_fields = ()

    inline = PlainInline(Album, site)
    formset_class = inline.get_formset(request_)

    assert not isinstance(formset_class.form.base_fields["is_primary"].widget, RadioCheckboxInput)


def test_non_boolean_field_raises_improperly_configured(request_, site):
    class BadInline(ExclusiveRadioFieldsMixin, djadmin.TabularInline):
        model = Image
        radio_select_exclusive_fields = ("title",)

    inline = BadInline(Album, site)

    with pytest.raises(ImproperlyConfigured, match="title"):
        inline.get_formset(request_)


def test_missing_field_raises_improperly_configured(request_, site):
    class BadInline(ExclusiveRadioFieldsMixin, djadmin.TabularInline):
        model = Image
        radio_select_exclusive_fields = ("does_not_exist",)

    inline = BadInline(Album, site)

    with pytest.raises(ImproperlyConfigured, match="does_not_exist"):
        inline.get_formset(request_)


def test_field_not_on_model_but_declared_on_form_is_radioized(request_, site):
    # `approved` doesn't exist on the Image model at all — only on this
    # custom form. The mixin works off form.base_fields, never the
    # model, so this must work the same as any other configured field.
    class ExtraFieldForm(forms.ModelForm):
        approved = forms.BooleanField(required=False)

        class Meta:
            model = Image
            fields = ["title", "is_primary", "approved"]

    class ExtraFieldInline(ExclusiveRadioFieldsMixin, djadmin.TabularInline):
        model = Image
        form = ExtraFieldForm
        radio_select_exclusive_fields = ("approved",)

    inline = ExtraFieldInline(Album, site)
    formset_class = inline.get_formset(request_)

    assert isinstance(formset_class.form.base_fields["approved"].widget, RadioCheckboxInput)


def test_form_field_type_overriding_model_field_type_is_radioized(request_, site):
    # `title` is a plain CharField on the Image model, but a form is
    # free to redeclare it as something else entirely. What matters for
    # radio_select_exclusive_fields is the form's field type, not the
    # model's.
    class BooleanTitleForm(forms.ModelForm):
        title = forms.BooleanField(required=False)

        class Meta:
            model = Image
            fields = ["title", "is_primary"]

    class BooleanTitleInline(ExclusiveRadioFieldsMixin, djadmin.TabularInline):
        model = Image
        form = BooleanTitleForm
        radio_select_exclusive_fields = ("title",)

    inline = BooleanTitleInline(Album, site)
    formset_class = inline.get_formset(request_)

    assert isinstance(formset_class.form.base_fields["title"].widget, RadioCheckboxInput)


def test_readonly_fields_are_excluded_by_default(request_, site):
    class PartlyReadonlyInline(ExclusiveRadioFieldsMixin, djadmin.TabularInline):
        model = Image
        radio_select_exclusive_fields = ("is_primary", "is_featured")
        readonly_fields = ("is_primary",)

    inline = PartlyReadonlyInline(Album, site)

    assert inline.get_radio_select_exclusive_fields(request_) == ("is_featured",)


def test_readonly_field_does_not_crash_get_formset(request_, site):
    # Without the get_readonly_fields filter, this would raise
    # ImproperlyConfigured for a field the admin class itself excluded
    # from the form (Django never puts a readonly field in
    # form.base_fields), even though nothing here is actually
    # misconfigured.
    class PartlyReadonlyInline(ExclusiveRadioFieldsMixin, djadmin.TabularInline):
        model = Image
        radio_select_exclusive_fields = ("is_primary", "is_featured")
        readonly_fields = ("is_primary",)

    inline = PartlyReadonlyInline(Album, site)
    formset_class = inline.get_formset(request_)

    assert "is_primary" not in formset_class.form.base_fields
    assert isinstance(formset_class.form.base_fields["is_featured"].widget, RadioCheckboxInput)


def test_get_radio_select_exclusive_fields_overrides_the_attribute(request_, site):
    class DynamicInline(ExclusiveRadioFieldsMixin, djadmin.TabularInline):
        model = Image
        radio_select_exclusive_fields = ("title",)  # would raise if actually used

        def get_radio_select_exclusive_fields(self, request, obj=None):
            return ("is_primary",)

    inline = DynamicInline(Album, site)
    formset_class = inline.get_formset(request_)

    assert isinstance(formset_class.form.base_fields["is_primary"].widget, RadioCheckboxInput)


def test_media_is_pulled_in_by_the_rendered_formset_when_a_field_is_radioized(request_, site):
    # Not `inline.media` itself: that's computed the same way regardless
    # of whether this inline is actually radio-configured, so it can't
    # be the thing gating "only load the JS when it's actually used".
    # The widget carries its own media, which a rendered formset (or
    # form) picks up automatically only because the widget is present.
    inline = ImageTabularInline(Album, site)
    formset_class = inline.get_formset(request_)
    js_paths = [str(s) for s in formset_class().media._js]

    assert any("django_admin_radio_select/radio-select.js" in p for p in js_paths)


def test_media_is_absent_when_no_field_is_radioized(request_, site):
    class PlainInline(ExclusiveRadioFieldsMixin, djadmin.TabularInline):
        model = Image
        radio_select_exclusive_fields = ()

    inline = PlainInline(Album, site)
    formset_class = inline.get_formset(request_)
    js_paths = [str(s) for s in formset_class().media._js]

    assert not any("django_admin_radio_select/radio-select.js" in p for p in js_paths)
