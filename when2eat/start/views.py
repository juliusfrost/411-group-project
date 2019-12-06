from django.shortcuts import render, redirect
from .models import UserProfile

def start(request):
    """
    Launch page for the web app. If the user does not have a profile,
    create one. If user already belongs to a session, redirect them
    to the session's page.
    """
    if request.user.is_authenticated:
        if not UserProfile.objects.filter(id=request.user).exists():
            newProfile = UserProfile(id=request.user)
            newProfile.save()
        else:
            profile = UserProfile.objects.get(id=request.user)
            session_id = profile.session_id
            if session_id:
                return redirect('/session/sessionPage/'+session_id)

        # Used to show warnings when joining a session fails
        context = {"invalidID": "false"}
        if "invalidID" in request.session:
            context["invalidID"] = "true"
            del request.session["invalidID"]

        return render(request, 'start/launchPage.html', context)
    return redirect('/')

# def hostSession(request):
#     return redirect('/session/host/weekselect')
#
# def joinSession(request):
#     return redirect('/session/join/validatesession')
