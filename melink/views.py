import re

from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LinkForm, ProfileForm
from .models import Profile


def index(request):
    return render(request, "melink/index.html")


def create(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES)

        if form.is_valid():
            profile = form.save()
            request.session["profile_id"] = profile.id
            return redirect("create_links")
    else:
        form = ProfileForm()

    return render(request, "melink/create.html", {"form": form})


def create_links(request):
    profile_id = request.session.get("profile_id")

    if profile_id is None:
        return redirect("create")

    profile = get_object_or_404(Profile, id=profile_id)

    if request.method == "POST":
        numbers = []

        # Знаходимо номери карток: link_1_title, link_3_title тощо.
        for key in request.POST:
            match = re.fullmatch(r"link_(\d+)_title", key)

            if match:
                numbers.append(int(match.group(1)))

        numbers = sorted(set(numbers))

        valid_forms = []
        form_errors = []

        # Створюємо окрему LinkForm для кожної картки.
        for number in numbers:
            title = request.POST.get(f"link_{number}_title", "").strip()
            url = request.POST.get(f"link_{number}_url", "").strip()

            # Порожню картку не зберігаємо. Це стосується і
            # початкових прикладів, якщо для них не ввели URL.
            if not url:
                continue

            form = LinkForm({
                "title": title,
                "url": url,
            })

            if form.is_valid():
                valid_forms.append(form)
            else:
                form_errors.append(
                    f"Посилання №{number}: {form.errors.as_text()}"
                )

        if form_errors:
            return render(
                request,
                "melink/create_links.html",
                {"form_errors": form_errors},
            )

        # Замінюємо попередній список тільки після перевірки всіх карток.
        with transaction.atomic():
            profile.links.all().delete()

            for sort_order, form in enumerate(valid_forms, start=1):
                link = form.save(commit=False)
                link.profile = profile
                link.sort_order = sort_order
                link.save()

        return redirect("public_profile", address=profile.address)

    return render(request, "melink/create_links.html")

def public_profile(request, address):
    profile = get_object_or_404(Profile, address=address)
    links = profile.links.order_by("sort_order")
    return render(
        request,
        "melink/public_profile.html",
        {
            "profile": profile,
            "links": links
        },
    )