from django.contrib.auth.models import User
from django.shortcuts import render

def home(request):
    return render(request, "home.html", {
        'users': User.objects.all()
    })

def search(request):
    raise NotImplementedError()
