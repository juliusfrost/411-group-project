from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def start(request):
    context = {}
    if request.user.is_authenticated:
        context["authtest"] = "You logged in!"
    return render(request, 'start/index.html', context)
