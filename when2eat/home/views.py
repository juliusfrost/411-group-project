from django.shortcuts import render, redirect
from django.contrib.auth import logout

def home(request):
    """
    Front page of the Web App. If user is already authenticated,
    redirect to home page.
    """
    if request.user.is_authenticated:
        return redirect('/start')
    return render(request, 'home/home.html')

def logout_view(request):
    """
    Logout redirect for OAuth2
    """
    logout(request)
    return redirect('/')
