"""Real-browser end-to-end tests: the JS module and the server-side
validation are unit-tested elsewhere (tests/js/, test_formsets.py); this
file is about the two only working together, through an actual browser,
against a real running Django server.
"""

import pytest
from gallery.models import Album, Image
from playwright.sync_api import Page, expect


class _AdminE2ETestCase:
    """Shared setup for browser tests against the example admin: log in
    once per test and build the Album/Image fixtures most of them start
    from, instead of each test repeating the same few lines.
    """

    def login(self, page: Page, live_server, django_user_model) -> None:
        django_user_model.objects.create_superuser("admin", "admin@example.com", "password")
        page.goto(f"{live_server.url}/admin/login/")
        page.fill('input[name="username"]', "admin")
        page.fill('input[name="password"]', "password")
        page.click('input[type="submit"]')
        expect(page).to_have_url(f"{live_server.url}/admin/")

    def create_album(self, *, images: tuple[tuple[str, bool], ...] = ()) -> Album:
        album = Album.objects.create(title="Holiday")
        for title, is_primary in images:
            Image.objects.create(album=album, title=title, is_primary=is_primary)
        return album

    def open_change_page(self, page: Page, live_server, album: Album) -> None:
        page.goto(f"{live_server.url}/admin/gallery/album/{album.pk}/change/")


@pytest.mark.django_db(transaction=True)
class TestInlineExclusivity(_AdminE2ETestCase):
    def test_selecting_one_row_unchecks_the_others_in_the_browser(
        self, page: Page, live_server, django_user_model
    ):
        album = self.create_album(images=(("Beach", True), ("Mountain", False), ("City", False)))
        self.login(page, live_server, django_user_model)
        self.open_change_page(page, live_server, album)

        beach = page.locator('input[name="images-0-is_primary"]')
        mountain = page.locator('input[name="images-1-is_primary"]')
        city = page.locator('input[name="images-2-is_primary"]')

        expect(beach).to_be_checked()

        mountain.check()

        expect(mountain).to_be_checked()
        expect(beach).not_to_be_checked()
        expect(city).not_to_be_checked()

    def test_saving_after_switching_the_row_persists(
        self, page: Page, live_server, django_user_model
    ):
        album = self.create_album(images=(("Beach", True), ("Mountain", False)))
        self.login(page, live_server, django_user_model)
        self.open_change_page(page, live_server, album)

        page.locator('input[name="images-1-is_primary"]').check()
        page.locator('input[name="_save"]').click()

        expect(page).to_have_url(f"{live_server.url}/admin/gallery/album/")
        images = {image.title: image.is_primary for image in album.images.all()}
        assert images == {"Beach": False, "Mountain": True}

    def test_dynamically_added_row_joins_the_exclusive_group(
        self, page: Page, live_server, django_user_model
    ):
        # Not a row we built ourselves: clicking Django admin's own "Add
        # another" button (inlines.js), same as a real user would, to
        # prove the delegated JS listener picks up a node it never saw
        # at load time.
        album = self.create_album(images=(("Beach", True),))
        self.login(page, live_server, django_user_model)
        self.open_change_page(page, live_server, album)

        beach = page.locator('input[name="images-0-is_primary"]')
        expect(beach).to_be_checked()

        total_forms = page.locator('input[name="images-TOTAL_FORMS"]')
        new_index = int(total_forms.input_value())

        page.get_by_role("button", name="Add another Image").click()

        expect(total_forms).to_have_value(str(new_index + 1))
        new_row_title = page.locator(f'input[name="images-{new_index}-title"]')
        new_row_primary = page.locator(f'input[name="images-{new_index}-is_primary"]')
        expect(new_row_title).to_be_visible()

        new_row_title.fill("Sunset")
        new_row_primary.check()

        expect(new_row_primary).to_be_checked()
        expect(beach).not_to_be_checked()

    def test_saving_after_adding_a_new_row_persists_it_as_the_selected_one(
        self, page: Page, live_server, django_user_model
    ):
        album = self.create_album(images=(("Beach", True),))
        self.login(page, live_server, django_user_model)
        self.open_change_page(page, live_server, album)

        total_forms = page.locator('input[name="images-TOTAL_FORMS"]')
        new_index = int(total_forms.input_value())

        page.get_by_role("button", name="Add another Image").click()
        page.locator(f'input[name="images-{new_index}-title"]').fill("Sunset")
        page.locator(f'input[name="images-{new_index}-is_primary"]').check()
        page.locator('input[name="_save"]').click()

        expect(page).to_have_url(f"{live_server.url}/admin/gallery/album/")
        images = {image.title: image.is_primary for image in album.images.all()}
        assert images == {"Beach": False, "Sunset": True}


@pytest.mark.django_db(transaction=True)
class TestChangelistExclusivity(_AdminE2ETestCase):
    def test_selecting_one_row_unchecks_the_others_in_the_browser(
        self, page: Page, live_server, django_user_model
    ):
        Album.objects.create(title="Winter", is_featured=True)
        Album.objects.create(title="Spring", is_featured=False)

        self.login(page, live_server, django_user_model)
        page.goto(f"{live_server.url}/admin/gallery/album/")

        # Don't assume row order matches creation order (the
        # changelist's own default ordering isn't this package's
        # concern): just track which row is checked by identity.
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
