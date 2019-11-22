from django.shortcuts import render, redirect
from django.contrib.auth import logout

def index(request):
    if request.user.is_authenticated:
        return redirect('/start')
    else:
        return render(request, 'home/index.html')

def logout_view(request):
    logout(request)
    return redirect('/')
