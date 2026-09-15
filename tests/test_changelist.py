import pytest
from django.contrib import admin as djadmin
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ImproperlyConfigured
from django.test import Client, RequestFactory
from django.urls import reverse
from gallery.admin import AlbumAdmin
from gallery.models import Album

from django_admin_radio_select import RadioSelectMixin
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
def albums():
    return [
        Album.objects.create(title="Winter", is_featured=True),
        Album.objects.create(title="Spring", is_featured=False),
        Album.objects.create(title="Summer", is_featured=False),
    ]


def test_list_editable_boolean_field_becomes_radio_input(request_, site):
    album_admin = AlbumAdmin(Album, site)
    formset_class = album_admin.get_changelist_formset(request_)
    field = formset_class.form.base_fields["is_featured"]

    assert isinstance(field.widget, RadioCheckboxInput)
    assert field.required is False


def test_changelist_group_key_uses_the_plain_formset_prefix(request_, site):
    # Unlike an inline formset (prefixed by relation name), a plain
    # list_editable formset defaults to Django's generic "form" prefix
    # -- the same group-key formula still applies unchanged.
    album_admin = AlbumAdmin(Album, site)
    formset_class = album_admin.get_changelist_formset(request_)
    group = formset_class.form.base_fields["is_featured"].widget.attrs["data-radio-select-group"]

    assert formset_class.get_default_prefix() == "form"
    assert group == "form::is_featured"


def test_rows_keep_independent_names_and_initial_state(request_, site, albums):
    album_admin = AlbumAdmin(Album, site)
    formset_class = album_admin.get_changelist_formset(request_)
    formset = formset_class(queryset=Album.objects.order_by("pk"))
    html = str(formset)

    assert 'name="form-0-is_featured"' in html
    assert 'name="form-1-is_featured"' in html

    rows = {form.instance.title: form for form in formset.forms}
    assert "checked" in str(rows["Winter"]["is_featured"])
    assert "checked" not in str(rows["Spring"]["is_featured"])


def test_unconfigured_modeladmin_is_left_alone(request_, site):
    class PlainAlbumAdmin(RadioSelectMixin, djadmin.ModelAdmin):
        list_display = ("title", "is_featured")
        list_editable = ("is_featured",)
        radio_select_exclusive_fields = ()

    album_admin = PlainAlbumAdmin(Album, site)
    formset_class = album_admin.get_changelist_formset(request_)

    assert not isinstance(formset_class.form.base_fields["is_featured"].widget, RadioCheckboxInput)


def test_field_missing_from_list_editable_raises_improperly_configured(request_, site):
    class BadAlbumAdmin(RadioSelectMixin, djadmin.ModelAdmin):
        list_display = ("title",)
        list_editable = ()
        radio_select_exclusive_fields = ("is_featured",)

    album_admin = BadAlbumAdmin(Album, site)

    with pytest.raises(ImproperlyConfigured, match="is_featured"):
        album_admin.get_changelist_formset(request_)


def test_media_is_pulled_in_by_the_rendered_formset_when_a_field_is_radioized(request_, site):
    # Not `album_admin.media` itself: that's the same regardless of
    # which view (changelist vs. change form) is asking, so it can't be
    # what scopes the JS to "only on the changelist, only if needed".
    album_admin = AlbumAdmin(Album, site)
    formset_class = album_admin.get_changelist_formset(request_)
    js_paths = [str(s) for s in formset_class(queryset=Album.objects.none()).media._js]

    assert any("django_admin_radio_select/radio-select.js" in p for p in js_paths)


def test_media_is_absent_from_the_plain_admin_media(site):
    # The plain ModelAdmin.media (used for every page, including the
    # regular add/change form) must NOT carry this script — only a
    # formset that actually contains the radioized field does.
    album_admin = AlbumAdmin(Album, site)
    js_paths = [str(s) for s in album_admin.media._js]

    assert not any("django_admin_radio_select/radio-select.js" in p for p in js_paths)


@pytest.fixture
def admin_client(django_user_model):
    django_user_model.objects.create_superuser("admin", "admin@example.com", "password")
    client = Client()
    client.login(username="admin", password="password")
    return client


def _base_post_data(albums):
    data = {
        "form-TOTAL_FORMS": str(len(albums)),
        "form-INITIAL_FORMS": str(len(albums)),
        "form-MIN_NUM_FORMS": "0",
        "form-MAX_NUM_FORMS": "1000",
        "_save": "Save",
    }
    for index, album in enumerate(albums):
        data[f"form-{index}-id"] = str(album.pk)
        if album.is_featured:
            data[f"form-{index}-is_featured"] = "on"
    return data


def test_changelist_renders_radio_inputs(admin_client, albums):
    response = admin_client.get(reverse("admin:gallery_album_changelist"))

    assert response.status_code == 200
    content = response.content.decode()
    assert 'type="radio"' in content
    assert 'data-radio-select-group="form::is_featured"' in content


def test_switching_the_featured_album_and_saving_persists_through_the_admin_view(
    admin_client, albums
):
    data = _base_post_data(albums)
    del data["form-0-is_featured"]  # Winter was featured
    data["form-1-is_featured"] = "on"  # Spring becomes featured

    response = admin_client.post(reverse("admin:gallery_album_changelist"), data)

    assert response.status_code == 302
    featured = {album.title: album.is_featured for album in Album.objects.all()}
    assert featured == {"Winter": False, "Spring": True, "Summer": False}


def test_posting_two_featured_albums_is_rejected_by_the_admin_view(admin_client, albums):
    data = _base_post_data(albums)
    data["form-1-is_featured"] = "on"  # Winter already featured; now Spring too

    response = admin_client.post(reverse("admin:gallery_album_changelist"), data)

    assert response.status_code == 200  # re-rendered with errors, not redirected
    assert not Album.objects.get(title="Spring").is_featured
