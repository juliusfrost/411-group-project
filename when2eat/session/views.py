from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.apps import apps
from django.contrib.auth.models import User
from social_django.models import UserSocialAuth
from .models import EatSession
from .filters import UserTable
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from uuid import uuid4
import time, datetime, json

SCOPES = ['https://www.googleapis.com/auth/calendar']

def weekSelect(request):
    if request.user.is_authenticated:
        return render(request, 'session/week.html')
    else:
        return redirect('/')

def validateSession(request):
    if request.user.is_authenticated:
        return render(request, 'session/join.html')
    else:
        return redirect('/')

def hostPersonal(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            startdate = request.POST.get("start")
            request.session["startdate"] = startdate
        return render(request, 'session/personal.html', {"button": getPersonalButton(True)})
    else:
        return redirect('/')

def joinPersonal(request):
    if request.user.is_authenticated:
        session_id = request.POST.get("sessionid")
        if EatSession.objects.filter(session_id=session_id).exists():
            session = EatSession.objects.get(session_id=session_id)
            if not session.locked:
                request.session["session_id"] = session_id
                return render(request, 'session/personal.html', {"button": getPersonalButton(False)})

        messages.add_message(request, messages.INFO, "Session locked or invalid")
        return redirect('/session/join/validatesession/')
    else:
        return redirect('/')

def createSession(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            while True:
                uid = str(uuid4())
                if not EatSession.objects.filter(session_id=uid).exists():
                    break
            #TODO Check NULL
            startdate = request.session["startdate"]
            startdate, enddate = getEndDate(startdate)
            week = startdate + " - " + enddate
            record = EatSession(session_id=uid, timeframe=week, locked=False)
            record.save()

            #TODO Better location settings
            loc = request.POST.get("location")
            res = request.POST.get("cuisine")
            price = request.POST.get("price")
            diet = request.POST.getlist("restriction")

            pref = {}
            pref["location"] = loc
            pref["cuisine"] = res
            pref["price"] = price
            pref["diet"] = diet

            print(startdate, enddate)
            avail = getCal(request, startdate, enddate)

            jsonPref = json.dumps(pref)
            jsonAvail = json.dumps(avail)

            UserProfile = apps.get_model("start", "UserProfile")

            if not UserProfile.objects.filter(id=request.user).exists():
                newProfile = UserProfile(id=request.user)
                newProfile.save()

            prof = UserProfile.objects.get(id=request.user)
            prof.session = record
            prof.host = True
            prof.availability = jsonAvail
            prof.preferences = jsonPref
            prof.save()

            return redirect('/session/sessionpage/'+uid)
    return redirect('/')


def joinSession(request):
    if request.user.is_authenticated:
        if request.method == "POST":

            #TODO Better location settings
            loc = request.POST.get("location")
            res = request.POST.get("cuisine")
            price = request.POST.get("price")
            diet = request.POST.getlist("restriction")

            pref = {}
            pref["location"] = loc
            pref["cuisine"] = res
            pref["price"] = price
            pref["diet"] = diet

            session_id = request.session["session_id"]
            session = EatSession.objects.get(session_id=session_id)

            date = session.timeframe
            startdate = date[:10]
            enddate = date[13:]

            avail = getCal(request, startdate, enddate)

            jsonAvail = json.dumps(avail)
            jsonPref = json.dumps(pref)

            UserProfile = apps.get_model("start", "UserProfile")

            if not UserProfile.objects.filter(id=request.user).exists():
                newProfile = UserProfile(id=request.user)
                newProfile.save()

            prof = UserProfile.objects.get(id=request.user)
            prof.session = session
            prof.host = False
            prof.availability = jsonAvail
            prof.preferences = jsonPref
            prof.save()

            return redirect('/session/sessionpage/'+session_id)
    return redirect('/')

def sessionPage(request, session_id):
    if request.user.is_authenticated:
        session = EatSession.objects.get(session_id=session_id)
        week = session.timeframe
        lock = session.locked
        UserProfile = apps.get_model("start", "UserProfile")
        sessionUsers = UserProfile.objects.filter(session=session_id)
        host = sessionUsers.get(host=True)
        qs = User.objects.filter(id__in=sessionUsers)
        table = UserTable(qs, orderable=False)
        context = {"table": table, "week": week, "id": session_id}
        if request.user.pk == host.pk:
            context["button"] = getCloseButton(lock)
        return render(request, 'session/session.html', context)
    return redirect('/')

def lockSession(request, session_id):
    print(session_id)
    if request.user.is_authenticated:
        if request.method == "POST":
            session = EatSession.objects.get(session_id=session_id)
            session.locked = True
            session.save()
        return redirect('/session/sessionpage/'+session_id)
    return redirect('/')

def solveSession(request, session_id):
    if request.user.is_authenticated:
        if request.method == "POST":
            session = EatSession.objects.get(session_id=session_id)
            session.delete()
    return redirect('/')

def getEndDate(startdate):
    #YYYY, MM, DD
    if startdate == "":
        #TODO: Local date not utc date
        sd = datetime.datetime.today()
        delta = datetime.timedelta(days = 1)
        sd = sd + delta
    else:
        sd = startdate.split('-')
        sd = [int(i) for i in sd]
        sd = datetime.datetime(sd[0], sd[1], sd[2])

    delta = datetime.timedelta(days = 6)
    ed = sd + delta
    start = str(sd.year) + "-" + str(sd.month) + "-" + str(sd.day)
    end = str(ed.year) + "-" + str(ed.month) + "-" + str(ed.day)
    return (start, end)

def getCal(request, startdate, enddate):
    context = {}
    if request.user.is_authenticated:
        pk = request.user.pk
        auth = UserSocialAuth.objects.filter(user_id = pk)
        authvals = auth.values()
        token = authvals[0]["extra_data"]["access_token"]
        refresh = authvals[0]["extra_data"]["refresh_token"]

        creds = Credentials(token, refresh_token=refresh,
                 token_uri=settings.TOKEN_URI,
                 client_id=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
                 client_secret=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
                 scopes=SCOPES)

        if creds.expired:
            creds.refresh(Request())

        service = build("calendar", "v3", credentials = creds)

        lt = time.localtime()
        offmins = int(time.altzone / 60)
        offhours = int(offmins/60)
        offmins -= offhours * 60
        offhours = offhours + (0 if lt.tm_isdst == 1 else 1)

        offmins = str(offmins)
        offhours = str(offhours)

        offmins = '0' + offmins if len(offmins) == 1 else offmins
        offhours = '0' + offhours if len(offhours) == 1 else offhours

        offset = '-{}:{}'.format(offhours, offmins)

        startdate += 'T08:00:00' + offset
        enddate += 'T22:00:00' + offset

        events_result = service.events().list(calendarId='primary',
                                        timeMin=startdate, timeMax=enddate,
                                        singleEvents=True,
                                        orderBy='startTime').execute()

        events = events_result.get('items', [])

        eventlst = []
        if not events:
            pass
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            eventlst.append((start, end))

        parsed = parseDateTime(eventlst)

    return parsed
#Assume no overlaping events and no cross day events
def parseDateTime(events):
    freeTime = {"Monday": ["08:00:00-22:00:00"],
                "Tuesday": ["08:00:00-22:00:00"],
                "Wednesday": ["08:00:00-22:00:00"],
                "Thursday": ["08:00:00-22:00:00"],
                "Friday": ["08:00:00-22:00:00"],
                "Saturday": ["08:00:00-22:00:00"],
                "Sunday": ["08:00:00-22:00:00"]}

    for start, end in events:
        stdate = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S%z")
        eddate = datetime.datetime.strptime(end, "%Y-%m-%dT%H:%M:%S%z")
        weekday = stdate.strftime('%A')
        freeTime[weekday] = splitTime(freeTime[weekday],
                              stdate.strftime('%H:%M:%S'),
                              eddate.strftime('%H:%M:%S'))
    return freeTime

def splitTime(current, start, end):
    toSplit = current[-1]
    endpoints = toSplit.split("-")
    t1 = "{}-{}".format(endpoints[0], start)
    t2 = "{}-{}".format(end, endpoints[1])
    current[-1] = t1
    current.append(t2)
    return current

def getPersonalButton(create):
    if create:
        return '''
               <button class="btn btn-outline-secondary" type="submit"
               onclick="this.form.action='createsession/';">Create</button>
               '''
    else:
        return '''
               <button class="btn btn-outline-secondary" type="submit"
               onclick="this.form.action='joinsession/';">Join</button>
               '''

def getCloseButton(lock):
    print(type(lock))
    if lock:
        print("solve")
        return '''
               <button class="btn btn-outline-secondary" type="submit"
               onclick="this.form.action='solvesession/';">Calculcate</button>
               '''
    else:
        print("lock")
        return '''
               <button class="btn btn-outline-secondary" type="submit"
               onclick="this.form.action='locksession/';">Lock</button>
               '''
