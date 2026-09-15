"""Real-browser end-to-end tests: the JS module and the server-side
validation are unit-tested elsewhere (tests/js/, test_formsets.py); this
file is about the two only working together, through an actual browser,
against a real running Django server.
"""

import pytest
from gallery.models import Album, Image
from playwright.sync_api import Page, expect


def _login(page: Page, base_url: str, django_user_model) -> None:
    django_user_model.objects.create_superuser("admin", "admin@example.com", "password")
    page.goto(f"{base_url}/admin/login/")
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "password")
    page.click('input[type="submit"]')
    expect(page).to_have_url(f"{base_url}/admin/")


@pytest.mark.django_db(transaction=True)
def test_selecting_one_inline_row_unchecks_the_others_in_the_browser(
    page: Page, live_server, django_user_model
):
    album = Album.objects.create(title="Holiday")
    Image.objects.create(album=album, title="Beach", is_primary=True)
    Image.objects.create(album=album, title="Mountain", is_primary=False)
    Image.objects.create(album=album, title="City", is_primary=False)

    _login(page, live_server.url, django_user_model)
    page.goto(f"{live_server.url}/admin/gallery/album/{album.pk}/change/")

    beach = page.locator('input[name="images-0-is_primary"]')
    mountain = page.locator('input[name="images-1-is_primary"]')
    city = page.locator('input[name="images-2-is_primary"]')

    expect(beach).to_be_checked()

    mountain.check()

    expect(mountain).to_be_checked()
    expect(beach).not_to_be_checked()
    expect(city).not_to_be_checked()


@pytest.mark.django_db(transaction=True)
def test_saving_after_switching_the_inline_row_persists(page: Page, live_server, django_user_model):
    album = Album.objects.create(title="Holiday")
    Image.objects.create(album=album, title="Beach", is_primary=True)
    Image.objects.create(album=album, title="Mountain", is_primary=False)

    _login(page, live_server.url, django_user_model)
    page.goto(f"{live_server.url}/admin/gallery/album/{album.pk}/change/")

    page.locator('input[name="images-1-is_primary"]').check()
    page.locator('input[name="_save"]').click()

    expect(page).to_have_url(f"{live_server.url}/admin/gallery/album/")
    images = {image.title: image.is_primary for image in album.images.all()}
    assert images == {"Beach": False, "Mountain": True}


@pytest.mark.django_db(transaction=True)
def test_selecting_one_changelist_row_unchecks_the_others_in_the_browser(
    page: Page, live_server, django_user_model
):
    Album.objects.create(title="Winter", is_featured=True)
    Album.objects.create(title="Spring", is_featured=False)

    _login(page, live_server.url, django_user_model)
    page.goto(f"{live_server.url}/admin/gallery/album/")

    # Don't assume row order matches creation order (the changelist's
    # own default ordering isn't this package's concern): just track
    # which row is checked by identity, before and after.
    group_selector = 'input[data-radio-select-group="form::is_featured"]'
    expect(page.locator(group_selector)).to_have_count(2)
    checked = page.locator(f"{group_selector}:checked")
    unchecked = page.locator(f"{group_selector}:not(:checked)")
    expect(checked).to_have_count(1)
    checked_name_before = checked.get_attribute("name")

    unchecked.check()

    checked_after = page.locator(f"{group_selector}:checked")
    expect(checked_after).to_have_count(1)
    assert checked_after.get_attribute("name") != checked_name_before
