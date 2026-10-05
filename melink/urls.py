from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path("create/", views.create, name="create"),
    path("create_links/", views.create_links, name="create_links"),
    path("profile/<slug:address>/", views.public_profile, name="public_profile"),

]
