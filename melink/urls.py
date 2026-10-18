from django.urls import path
from . import views

urlpatterns = [
    path(
        "api/profiles/",
        views.ProfileCreateAPIView.as_view(),
        name="api-profile-create",
    ),
    path("", views.index, name="home"),
    path("create/", views.create, name="create"),
    path("create_links/", views.create_links, name="create_links"),
    path("appearance/", views.appearance, name="appearance"),
    path("profile/<slug:address>/", views.public_profile, name="public_profile"),
    path(
        "api/v1/profiles/<slug:address>/",
        views.PublicProfileAPIView.as_view(),
        name="api-profile-detail",
    ),
]
