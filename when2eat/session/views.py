from django.shortcuts import render


# Create your views here.
def index(request):
    return render(request, 'session/index.html')


def create(request):
    return render(request, 'session/create.html')


def join(request):
    return render(request, 'session/join.html')
