from django.db import models

class Profile(models.Model):
    name = models.CharField(max_length=50)
    short_bio = models.CharField(max_length=50)
    about_me = models.CharField(max_length=160)
    address = models.SlugField(max_length=20, unique=True)
    photo_path = models.ImageField(upload_to="profile_photos/", max_length=255, blank=True)
    THEMES = [
        ("purple", "Фіолетова"),
        ("dark", "Темна"),
        ("light", "Світла"),
    ]
    theme = models.CharField(
        max_length=20,
        choices=THEMES,
        default="purple",
    )
    
    def __str__(self):
        return self.name


class Link(models.Model):
    profile = models.ForeignKey(
    Profile,
    on_delete=models.CASCADE,
    related_name="links",
    )
    title = models.CharField(max_length=50)
    url = models.CharField(max_length=500)
    sort_order = models.IntegerField()
