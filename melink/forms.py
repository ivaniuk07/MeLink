from .models import Profile
from django.forms import ModelForm

class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'short_bio', 'about_me', 'address', 'photo_path']