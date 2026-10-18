import re
from django.db import IntegrityError, transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from rest_framework import generics, permissions
from .forms import LinkForm, ProfileForm, ThemeForm
from .models import Link, Profile
from .serializers import ProfileCreateSerializer, ProfileSerializer


def owned_profile(request):
    return Profile.objects.filter(pk=request.session.get("profile_id")).first()


def index(request):
    return render(
        request, "melink/index.html", {"owned_profile": owned_profile(request)}
    )


@require_http_methods(["GET", "POST"])
def create(request):
    profile = owned_profile(request)
    form = ProfileForm(
        request.POST if request.method == "POST" else None,
        request.FILES if request.method == "POST" else None,
        instance=profile,
    )
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                profile = form.save()
        except IntegrityError:
            form.add_error("address", "Ця адреса вже зайнята. Обери іншу.")
        else:
            request.session["profile_id"] = profile.pk
            return redirect("create_links")
    return render(
        request,
        "melink/create.html",
        {
            "form": form,
            "profile": profile,
            "preview": True,
            "links": profile.links.filter(is_visible=True) if profile else [],
        },
    )


@require_http_methods(["GET", "POST"])
def create_links(request):
    profile = owned_profile(request)
    if profile is None:
        return redirect("create")
    errors = []
    if request.method == "POST":
        numbers = sorted(
            {
                int(match.group(1))
                for key in request.POST
                if (match := re.fullmatch(r"link_(\d+)_(?:title|url)", key))
            }
        )
        cards = [
            {
                "number": n,
                "title": request.POST.get(f"link_{n}_title", "").strip(),
                "url": request.POST.get(f"link_{n}_url", "").strip(),
                "is_visible": f"link_{n}_visible" in request.POST,
            }
            for n in numbers
        ]
        forms = []
        if len(cards) > 20:
            errors.append("Можна додати не більше 20 посилань.")
        else:
            for card in cards:
                if not card["title"] and not card["url"]:
                    continue
                form = LinkForm(card)
                if form.is_valid():
                    forms.append(form)
                else:
                    for field_errors in form.errors.values():
                        errors.extend(
                            f"Посилання №{card['number']}: {error}"
                            for error in field_errors
                        )
        if not errors:
            with transaction.atomic():
                profile.links.all().delete()
                for order, form in enumerate(forms, start=1):
                    link = form.save(commit=False)
                    link.profile = profile
                    link.sort_order = order
                    link.save()
            return redirect("appearance")
    else:
        cards = [
            {
                "number": i,
                "title": link.title,
                "url": link.url,
                "is_visible": link.is_visible,
            }
            for i, link in enumerate(profile.links.all(), start=1)
        ]
    if not cards:
        cards = [{"number": 1, "title": "", "url": "", "is_visible": True}]
    return render(
        request,
        "melink/create_links.html",
        {
            "profile": profile,
            "preview": True,
            "links": profile.links.filter(is_visible=True),
            "cards": cards,
            "form_errors": errors,
        },
    )


@require_http_methods(["GET", "POST"])
def appearance(request):
    profile = owned_profile(request)
    if profile is None:
        return redirect("create")
    form = ThemeForm(
        request.POST if request.method == "POST" else None, instance=profile
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("public_profile", address=profile.address)
    return render(
        request,
        "melink/appearance.html",
        {
            "profile": profile,
            "preview": True,
            "links": profile.links.filter(is_visible=True),
            "form": form,
        },
    )


def public_profile(request, address):
    profile = get_object_or_404(Profile, address=address)
    return render(
        request,
        "melink/public_profile.html",
        {
            "profile": profile,
            "links": profile.links.filter(is_visible=True),
            "is_owner": request.session.get("profile_id") == profile.pk,
            "public_url": request.build_absolute_uri(),
        },
    )

class PublicProfileAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    lookup_field = "address"
    queryset = Profile.objects.prefetch_related(
        Prefetch(
            "links",
            queryset=Link.objects.filter(is_visible=True),
            to_attr="visible_links",
        )
    )
    serializer_class = ProfileSerializer


class ProfileCreateAPIView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ProfileCreateSerializer
