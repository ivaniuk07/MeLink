from django.forms import ModelForm
from .models import Profile, Link


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ["name", "short_bio", "about_me", "address", "photo_path"]


class LinkForm(ModelForm):
    class Meta:
        model = Link
        fields = ["title", "url"]