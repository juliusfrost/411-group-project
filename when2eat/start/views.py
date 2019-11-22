from django.shortcuts import render, redirect
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from social_django.models import UserSocialAuth
from django.conf import settings
from .models import UserProfile
import time, datetime

SCOPES = ['https://www.googleapis.com/auth/calendar']

# Create your views here.
def start(request):
    context = {}
    if request.user.is_authenticated:
        context["authtest"] = "You logged in!"

        if not UserProfile.objects.filter(id=request.user).exists():
            newProfile = UserProfile(id=request.user)
            newProfile.save()
        else:
            profile = UserProfile.objects.get(id=request.user)
            session_id = profile.session_id
            if session_id:
                return redirect('/session/sessionpage/'+session_id)

        return render(request, 'start/index.html', context)
    else:
        return redirect('/')

def hostSession(request):
    return redirect('/session/host/weekselect')

def joinSession(request):
    return redirect('/session/join/validatesession')

def getCal(request):
    context = {}
    if request.user.is_authenticated:
        context["authtest"] = "You logged in!"

        pk = request.user.pk
        auth = UserSocialAuth.objects.filter(user_id = pk)
        authvals = auth.values()
        token = authvals[0]["extra_data"]["access_token"]
        refresh = authvals[0]["extra_data"]["refresh_token"]

        # creds = None
        # record = CredentialsModel.objects.filter(id_id = pk)

        # if len(record) == 0:
            # flow = InstalledAppFlow.from_client_secrets_file(
            #         '/Users/chris/Documents/CS411/Testing/when2eat (Postgres)/start/creds.json', SCOPES)
            # creds = flow.run_local_server()
        # else:
        #     pass

        creds = Credentials(token, refresh_token=refresh,
                 token_uri=settings.TOKEN_URI,
                 client_id=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
                 client_secret=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
                 scopes=SCOPES)

        # creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        # if os.path.exists('token.pickle'):
        #     with open('token.pickle', 'rb') as token:
        #         creds = pickle.load(token)
        #
        # # If there are no (valid) credentials available, let the user log in.
        # if not creds or not creds.valid:
        #     if creds and creds.expired and creds.refresh_token:
        #         creds.refresh(Request())
        #     else:
        #         flow = InstalledAppFlow.from_client_secrets_file(
        #             '/Users/chris/Documents/CS411/Testing/when2eat (Postgres)/start/creds.json', SCOPES)
        #         creds = flow.run_local_server(port=8001)
        #         # print(dir(flow))
        #     # Save the credentials for the next run
        #     with open('token.pickle', 'wb') as token:
        #         pickle.dump(creds, token)

        # record = CredentialsModel(id = auth[0], token = creds.token,
        #                             refresh = creds.refresh_token,
        #                             expiry = creds.expiry)
        #
        # record.save()

        if creds.expired:
            creds.refresh(Request())

        service = build("calendar", "v3", credentials = creds)

        startdate = '2019-11-18'

        sd = startdate.split('-')
        sd = [int(i) for i in sd]

        sd = datetime.datetime(sd[0], sd[1], sd[2])

        delta = datetime.timedelta(days = 6)
        ed = sd + delta

        enddate = str(ed.date())

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
        # now = datetime.datetime.utcnow().isoformat() + 'Z'

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

            # ex = '2011-06-03T10:00:00-07:00'
            # test = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S%z")
            # test2 = datetime.datetime.strptime(end, "%Y-%m-%dT%H:%M:%S%z")
            # test3 = test2 - test
            # print(test)
            # print(test2)
            # print(test3)
            # print(test3.seconds / 60)


        parsed = parseDateTime(eventlst)

        prettyParsed = 'Free Time:<br><br>'
        for key in parsed:
            prettyParsed += "{}:<br>".format(key)
            for slot in parsed[key]:
                prettyParsed += "\t{}<br>".format(slot)
            prettyParsed += "<br>"

        context["authtest"] = prettyParsed

    return render(request, 'start/events.html', context)

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
