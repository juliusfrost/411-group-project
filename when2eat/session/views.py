from django.shortcuts import render


# Create your views here.
def index(request):
    # request.user
    return render(request, 'session/index.html')


def create(request):
    return render(request, 'session/create.html')


def join(request):
    return render(request, 'session/join.html')


def join_session(request, session_id):
    return render(request, 'session/join.html')
