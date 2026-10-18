import io
import tempfile
from html.parser import HTMLParser
from PIL import Image
from django.contrib.staticfiles import finders
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from .forms import ProfileForm
from .models import Link, Profile


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.assets = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a":
            self.links.append(attrs.get("href", ""))
        if tag in {"script", "img", "link"}:
            self.assets.append(attrs.get("src", attrs.get("href", "")))


class ProfileFlowTests(TestCase):
    def setUp(self):
        self.data = {
            "name": "Олексій",
            "short_bio": "Python developer",
            "about_me": "Django and SQL",
            "address": "oleksii",
        }

    def create_profile(self):
        response = self.client.post(reverse("create"), self.data)
        self.assertRedirects(response, reverse("create_links"))
        return Profile.objects.get(address="oleksii")

    def test_home_has_two_working_create_links(self):
        page = PageParser()
        page.feed(self.client.get("/").content.decode())
        self.assertEqual(page.links.count(reverse("create")), 2)
        for href in page.links:
            if href.startswith("/") and not href.startswith("//"):
                self.assertEqual(self.client.get(href).status_code, 200)
        self.assertNotIn("#create", page.links)

    def test_complete_flow_and_owner_edit(self):
        profile = self.create_profile()
        self.assertRedirects(
            self.client.post(
                reverse("create_links"),
                {
                    "link_1_title": "GitHub",
                    "link_1_url": "https://github.com/ivaniuk07",
                    "link_1_visible": "on",
                    "link_2_title": "Hidden link",
                    "link_2_url": "https://example.com/hidden",
                },
            ),
            reverse("appearance"),
        )
        self.assertRedirects(
            self.client.post(reverse("appearance"), {"theme": "dark"}),
            reverse("public_profile", args=["oleksii"]),
        )
        profile.refresh_from_db()
        self.assertEqual(profile.theme, "dark")
        public = reverse("public_profile", args=["oleksii"])
        self.assertContains(self.client.get(public), "Редагувати")
        anonymous = Client().get(public)
        self.assertContains(anonymous, "https://github.com/ivaniuk07")
        self.assertNotContains(anonymous, "Hidden link")
        self.assertNotContains(anonymous, "Редагувати")
        self.assertEqual(profile.links.count(), 2)
        self.client.post(reverse("create"), {**self.data, "name": "Updated"})
        self.assertEqual(Profile.objects.count(), 1)
        profile.refresh_from_db()
        self.assertEqual(profile.name, "Updated")
        self.assertContains(self.client.get("/"), "Мій профіль")

    def test_edit_steps_require_session(self):
        for name in ["create_links", "appearance"]:
            self.assertRedirects(self.client.get(reverse(name)), reverse("create"))
            self.assertRedirects(
                self.client.post(reverse(name), {"profile_id": 1}), reverse("create")
            )

    def test_other_browser_cannot_take_existing_address(self):
        profile = self.create_profile()
        response = Client().post(
            reverse("create"), {**self.data, "address": "OLEKSII", "name": "Intruder"}
        )
        self.assertContains(response, "Ця адреса вже зайнята")
        profile.refresh_from_db()
        self.assertEqual(profile.name, "Олексій")
        self.assertEqual(Profile.objects.count(), 1)

    def test_invalid_profile_retains_input_and_empty_post_has_errors(self):
        response = self.client.post(
            reverse("create"), {**self.data, "address": "bad address"}
        )
        self.assertContains(response, "bad address")
        self.assertTrue(response.context["form"].errors)
        self.assertTrue(self.client.post(reverse("create"), {}).context["form"].errors)
        self.assertEqual(Profile.objects.count(), 0)

    def test_bad_link_does_not_delete_saved_links(self):
        profile = self.create_profile()
        Link.objects.create(
            profile=profile, title="Saved", url="https://example.com", sort_order=1
        )
        for bad_url in ["javascript:alert(1)", "ftp://example.com", "invalid"]:
            response = self.client.post(
                reverse("create_links"),
                {
                    "link_5_title": "Invalid",
                    "link_5_url": bad_url,
                    "link_5_visible": "on",
                },
            )
            self.assertTrue(response.context["form_errors"])
            self.assertContains(response, bad_url)
            self.assertEqual(profile.links.get().title, "Saved")

    def test_missing_title_is_invalid(self):
        profile = self.create_profile()
        response = self.client.post(
            reverse("create_links"), {"link_1_url": "https://example.com"}
        )
        self.assertTrue(response.context["form_errors"])
        self.assertFalse(profile.links.exists())

    def test_empty_rows_can_clear_links(self):
        profile = self.create_profile()
        Link.objects.create(
            profile=profile, title="Saved", url="https://example.com", sort_order=1
        )
        self.assertRedirects(
            self.client.post(
                reverse("create_links"), {"link_1_title": "", "link_1_url": ""}
            ),
            reverse("appearance"),
        )
        self.assertFalse(profile.links.exists())

    def test_link_limit(self):
        self.create_profile()
        data = {f"link_{n}_title": f"Link {n}" for n in range(21)}
        response = self.client.post(reverse("create_links"), data)
        self.assertContains(response, "не більше 20")
        self.assertFalse(Link.objects.exists())

    def test_sparse_link_numbers_preserve_order(self):
        profile = self.create_profile()
        self.client.post(
            reverse("create_links"),
            {
                "link_9_title": "Last",
                "link_9_url": "https://example.com/last",
                "link_2_title": "First",
                "link_2_url": "https://example.com/first",
            },
        )
        self.assertEqual(
            list(profile.links.values_list("title", flat=True)), ["First", "Last"]
        )

    def test_invalid_theme_does_not_change_profile(self):
        profile = self.create_profile()
        response = self.client.post(reverse("appearance"), {"theme": "unknown"})
        self.assertTrue(response.context["form"].errors)
        profile.refresh_from_db()
        self.assertEqual(profile.theme, "purple")
        self.assertTrue(
            self.client.post(reverse("appearance"), {}).context["form"].errors
        )

    def test_unknown_profile_returns_404(self):
        self.assertEqual(
            self.client.get(reverse("public_profile", args=["missing"])).status_code,
            404,
        )

    def test_all_flow_pages_reference_existing_static_files(self):
        self.create_profile()
        for url in [
            "/",
            "/create/",
            "/create_links/",
            "/appearance/",
            "/profile/oleksii/",
        ]:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            page = PageParser()
            page.feed(response.content.decode())
            for asset in page.assets:
                if asset.startswith("/static/"):
                    self.assertIsNotNone(
                        finders.find(asset.removeprefix("/static/")), asset
                    )

    def test_uploaded_photo_and_invalid_file(self):
        with tempfile.TemporaryDirectory() as directory, override_settings(
            MEDIA_ROOT=directory
        ):
            content = io.BytesIO()
            Image.new("RGB", (10, 10), "purple").save(content, format="PNG")
            image = SimpleUploadedFile(
                "avatar.png", content.getvalue(), content_type="image/png"
            )
            self.client.post(reverse("create"), {**self.data, "photo_path": image})
            profile = Profile.objects.get(address="oleksii")
            self.assertTrue(profile.photo_path.storage.exists(profile.photo_path.name))
            self.assertContains(
                self.client.get("/profile/oleksii/"), profile.photo_path.url
            )
            bad = SimpleUploadedFile(
                "fake.png", b"not an image", content_type="image/png"
            )
            form = ProfileForm(self.data, {"photo_path": bad}, instance=profile)
            self.assertFalse(form.is_valid())
            self.assertIn("photo_path", form.errors)

    def test_html_is_escaped(self):
        self.client.post(
            reverse("create"), {**self.data, "name": "<script>alert(1)</script>"}
        )
        response = self.client.get("/profile/oleksii/")
        self.assertNotContains(response, "<script>alert(1)</script>")
        self.assertContains(response, "&lt;script&gt;")


class PublicProfileAPITests(TestCase):
    def setUp(self):
        self.profile = Profile.objects.create(
            name="Олексій",
            short_bio="Python developer",
            about_me="Django and SQL",
            address="oleksii",
        )
        Link.objects.create(
            profile=self.profile,
            title="GitHub",
            url="https://github.com/ivaniuk07",
            sort_order=1,
            is_visible=True,
        )
        Link.objects.create(
            profile=self.profile,
            title="Hidden link",
            url="https://example.com/hidden",
            sort_order=2,
            is_visible=False,
        )

    def test_api_returns_public_profile_and_only_visible_links(self):
        response = self.client.get(reverse("api-profile-detail", args=["oleksii"]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Олексій")
        self.assertEqual(
            response.json()["links"],
            [
                {
                    "title": "GitHub",
                    "url": "https://github.com/ivaniuk07",
                    "sort_order": 1,
                }
            ],
        )

    def test_api_returns_404_for_unknown_profile(self):
        response = self.client.get(reverse("api-profile-detail", args=["missing"]))

        self.assertEqual(response.status_code, 404)

    def test_post_creates_profile_and_nested_links(self):
        response = self.client.post(
            reverse("api-profile-create"),
            {
                "name": "Новий профіль",
                "short_bio": "Python developer",
                "about_me": "Вивчаю Django",
                "address": "new-profile",
                "theme": "purple",
                "links": [
                    {"title": "GitHub", "url": "https://github.com/example"},
                    {"title": "Сайт", "url": "https://example.com"},
                ],
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        profile = Profile.objects.get(address="new-profile")
        self.assertEqual(profile.links.count(), 2)
        self.assertEqual(
            list(profile.links.values_list("sort_order", flat=True)), [1, 2]
        )
        self.assertEqual(len(response.json()["links"]), 2)

    def test_post_rejects_invalid_link_url(self):
        response = self.client.post(
            reverse("api-profile-create"),
            {
                "name": "Новий профіль",
                "short_bio": "Python developer",
                "about_me": "Вивчаю Django",
                "address": "invalid-link-profile",
                "links": [{"title": "Bad link", "url": "javascript:alert(1)"}],
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Profile.objects.filter(address="invalid-link-profile").exists())
