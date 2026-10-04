from django.shortcuts import render
from .models import Profile
from .forms import ProfileForm

def index(request):
    return render(request, "melink/index.html")

def create(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES)

        if form.is_valid():
            profile = form.save()
            # Тут пізніше зробимо перехід до кроку «Посилання».
    else:
        form = ProfileForm()

    return render(request, "melink/create.html", {"form": form})