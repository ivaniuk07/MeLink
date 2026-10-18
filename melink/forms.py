from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from .models import Link, Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["name", "short_bio", "about_me", "address", "photo_path"]
        labels = {
            "name": "Як тебе звати?",
            "short_bio": "Короткий підпис",
            "about_me": "Кілька слів про себе",
            "address": "Адреса твоєї сторінки",
            "photo_path": "Фото",
        }
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "id": "display-name",
                    "placeholder": "Олексій Іванюк",
                    "autocomplete": "name",
                }
            ),
            "short_bio": forms.TextInput(
                attrs={"id": "short-bio", "placeholder": "Python-розробник · Львів"}
            ),
            "about_me": forms.Textarea(
                attrs={
                    "id": "description",
                    "rows": 3,
                    "placeholder": "Розкажи про свої інтереси та проєкти.",
                }
            ),
            "address": forms.TextInput(
                attrs={
                    "id": "page-address",
                    "placeholder": "oleksii",
                    "autocomplete": "off",
                }
            ),
            "photo_path": forms.ClearableFileInput(
                attrs={"accept": "image/png,image/jpeg", "id": "photo"}
            ),
        }

    def clean_address(self):
        address = self.cleaned_data["address"].lower()
        existing = Profile.objects.filter(address__iexact=address).exclude(
            pk=self.instance.pk
        )
        if existing.exists():
            raise ValidationError("Ця адреса вже зайнята. Обери іншу.")
        return address

    def clean_photo_path(self):
        photo = self.cleaned_data.get("photo_path")
        if photo and hasattr(photo, "image"):
            if photo.size > 5 * 1024 * 1024:
                raise ValidationError("Фото має бути не більше 5 МБ.")
            if photo.image.format not in {"JPEG", "PNG"}:
                raise ValidationError("Завантаж фото у форматі JPG або PNG.")
        return photo


class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = ["title", "url", "is_visible"]

    def clean_url(self):
        url = self.cleaned_data["url"].strip()
        URLValidator(schemes=["http", "https"])(url)
        return url


class ThemeForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["theme"]
        widgets = {"theme": forms.RadioSelect}
        labels = {"theme": "Обери оформлення"}
