from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.apps import apps
from django.contrib.auth.models import User
from social_django.models import UserSocialAuth
from .models import EatSession
from .tables import UserTable
from . import formHandler as forms
from . import timeHandler
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from uuid import uuid4
import time, datetime, json, requests
from collections import Counter

def hostForms(request):
    """
    Get forms for session host.
    """
    if request.user.is_authenticated:
        context = {
            "title": "Start a Session",
            "forms": forms.getForms(True),
            "button": forms.getCreateOrJoinButton(True)
        }
        return render(request, 'session/sessionForms.html', context=context)
    return redirect('/')

def validateSessionID(request):
    """
    Validate the session id entered by a guest. If the session does not
    exist or is locked, redirect back to id input with error message.
    Otherwise, get forms for session guest.
    """
    if request.user.is_authenticated:
        if request.method == "POST":
            sessionID = request.POST.get("sessionID")
            if EatSession.objects.filter(session_id=sessionID).exists():
                session = EatSession.objects.get(session_id=sessionID)
                if not session.locked:
                    request.session["sessionID"] = sessionID
                    context = {
                        "title": "Join a Session",
                        "forms": forms.getForms(False),
                        "button": forms.getCreateOrJoinButton(False)
                    }
                    return render(request, 'session/sessionForms.html', context)
            else:
                messages.warning(request, "Session locked or invalid")
                request.session["invalidID"] = "true"
                return redirect('/start')
    return redirect('/')

def createSession(request):
    """
    Create a new session and update the host's profile with their new
    preferences, availabilities, and host status. Redirect to session
    page.
    """
    if request.user.is_authenticated:
        if request.method == "POST":

            # Generate unique UUID4 to be the sessionID
            # Do not search for more than 5 seconds
            timeout = time.time() + 5
            while True:
                uid = str(uuid4())
                if not EatSession.objects.filter(session_id=uid).exists():
                    break
                if time.time() > timout: #Took too long
                    redirect("/")

            name = request.POST.get("name")
            startDate = request.POST.get("date")
            location = request.POST.get("location")
            comments = json.dumps([])

            startDate, endDate = timeHandler.getEndDate(startDate)
            timeframe = startDate.strftime("%Y-%m-%d") + " - " + endDate.strftime("%Y-%m-%d")

            # Create new session and save to database
            session = EatSession(session_id=uid, timeframe=timeframe, locked=False,
                                name=name, location=location, comments=comments)
            session.save()

            # Get restaurant preferences
            cuisinePref = request.POST.get("cuisine")
            foodtypePref = request.POST.get("foodtype")
            pricePref = request.POST.get("price")

            # If user chose to block times, get all times
            timeBlocks = []
            if "timeselection" in request.POST:
                timeBlocks = request.POST.getlist("timeselection")

            preferences = {
                "cuisine": cuisinePref,
                "foodtype": foodtypePref,
                "price": pricePref
            }

            # Get availabilities
            calendarAvail = getCalendarAvailability(request, startDate)
            timeBlockAvail = timeHandler.getTimeBlockAvailability(timeBlocks)
            totalAvail = timeHandler.timeOverlap(calendarAvail, timeBlockAvail)

            jsonPref = json.dumps(preferences)
            jsonAvail = json.dumps(totalAvail)

            UserProfile = apps.get_model("start", "UserProfile")

            if not UserProfile.objects.filter(id=request.user).exists():
                newProfile = UserProfile(id=request.user)
                newProfile.save()

            # Update user profile with new information
            prof = UserProfile.objects.get(id=request.user)
            prof.session = session
            prof.host = True
            prof.availability = jsonAvail
            prof.preferences = jsonPref
            prof.save()

            return redirect('/session/sessionPage/'+uid)
    return redirect('/')


def joinSession(request):
    """
    Get the existing session and place the guest into it. Update the
    guest's profile with their new preferences and availabilities.
    Redirect to session page.
    """
    if request.user.is_authenticated:
        if request.method == "POST":

            # Get restaurant preferences
            cuisinePref = request.POST.get("cuisine")
            foodtypePref = request.POST.get("foodtype")
            pricePref = request.POST.get("price")

            # If user chose to block times, get all times
            timeBlocks = []
            if "timeselection" in request.POST:
                timeBlocks = request.POST.getlist("timeselection")

            preferences = {
                "cuisine": cuisinePref,
                "foodtype": foodtypePref,
                "price": pricePref
            }

            sessionID = request.session["sessionID"]
            session = EatSession.objects.get(session_id=sessionID)

            timeframe = session.timeframe
            startDate = timeframe.split(" - ")[0].split("-")
            startDate = [int(i) for i in startDate]
            startDate = datetime.datetime(startDate[0], startDate[1], startDate[2])

            # Get availabilities
            calendarAvail = getCalendarAvailability(request, startDate)
            timeBlockAvail = timeHandler.getTimeBlockAvailability(timeBlocks)
            totalAvail = timeHandler.timeOverlap(calendarAvail, timeBlockAvail)

            jsonPref = json.dumps(preferences)
            jsonAvail = json.dumps(totalAvail)

            UserProfile = apps.get_model("start", "UserProfile")

            if not UserProfile.objects.filter(id=request.user).exists():
                newProfile = UserProfile(id=request.user)
                newProfile.save()

            # Update user profile with new information
            prof = UserProfile.objects.get(id=request.user)
            prof.session = session
            prof.host = False
            prof.availability = jsonAvail
            prof.preferences = jsonPref
            prof.save()

            return redirect('/session/sessionPage/'+sessionID)
    return redirect('/')

def sessionPage(request, sessionID):
    """
    Show the session page for the specific session ID. Provide the host
    with buttons to lock or solve the session.
    """
    if request.user.is_authenticated:
        session = EatSession.objects.get(session_id=sessionID)

        # Grab session information
        name = session.name
        timeframe = session.timeframe
        lock = session.locked
        comments = json.loads(session.comments)
        comments.reverse()

        # Get the host and list of all session members
        UserProfile = apps.get_model("start", "UserProfile")
        sessionUsers = UserProfile.objects.filter(session=sessionID)
        host = sessionUsers.get(host=True)
        sessionUsers = User.objects.filter(id__in=sessionUsers)

        # Create the table of session members
        table = UserTable(sessionUsers, orderable=False)

        # Combine session elements
        context = {"sessionName": name,
                   "table": table,
                   "sessionTimeframe": timeframe,
                   "sessionID": sessionID,
                   "lock": lock,
                   "comments": comments}

        # If this is this host, give them appropriate buttons
        if request.user.pk == host.pk:
            context["button"] = forms.getLockOrSolveButton(lock)

        return render(request, 'session/sessionPage.html', context)
    return redirect('/')

def addComment(request, sessionID):
    """
    Add a public comment to the session page.
    """
    if request.user.is_authenticated:
        if request.method == "POST":
            newCommentText = request.POST.get("comment")

            # Do not accept empty comments
            if len(newCommentText) > 0:
                session = EatSession.objects.get(session_id=sessionID)
                comments = json.loads(session.comments)

                # Build new comment
                newComment = {
                    "author": "{} {}".format(request.user.first_name, request.user.last_name),
                    "text": newCommentText
                }

                # Add new comment and save session
                comments.append(newComment)
                session.comments = json.dumps(comments)
                session.save()
        return redirect('/session/sessionPage/'+sessionID)
    return redirect('/')

def lockSession(request, sessionID):
    """
    Lock an active session to prevent new members from joining.
    """
    if request.user.is_authenticated:
        if request.method == "POST":
            session = EatSession.objects.get(session_id=sessionID)
            session.locked = True
            session.save()
        return redirect('/session/sessionPage/'+sessionID)
    return redirect('/')

def solveSession(request, sessionID):
    """
    Solve an active session by finding a common time for session members
    and a business open at that time and matching the most common preferences.
    Give priority to members who are indicated to be "must attend."
    """
    if request.user.is_authenticated:
        if request.method == "POST":
            session = EatSession.objects.get(session_id=sessionID)
            timeframe = session.timeframe
            location = session.location

            # Get first day of the session
            firstDay = timeframe.split(" - ")[0]
            firstDay = firstDay.split('-')
            firstDay = [int(i) for i in firstDay]
            firstDay = datetime.datetime(firstDay[0], firstDay[1], firstDay[2])

            UserProfile = apps.get_model("start", "UserProfile")
            sessionUsers = UserProfile.objects.filter(session=sessionID).values()

            # Initalize lists with preferences for attendees
            cuisinePref = []
            foodTypePref = []
            pricePref = []

            # Get the list of ids for the "must attend" members
            mandatoryAttendees = request.POST.getlist("selection")
            mandatoryAttendees = [int(id) for id in mandatoryAttendees]

            # Compute
            availTimes = None
            for user in sessionUsers:
                if user["id_id"] in mandatoryAttendees:
                    availability = json.loads(user["availability"])
                    preferences = json.loads(user["preferences"])
                    cuisinePref.append(preferences["cuisine"])
                    foodTypePref.append(preferences["foodtype"])
                    pricePref.append(preferences["price"])
                    if availTimes == None:
                        availTimes = availability
                    else:
                        availTimes = timeHandler.timeOverlap(availTimes, availability)

            chosenTime = None
            chosenDay = None

            if availTimes == None:
                if len(mandatoryAttendees) > 0:
                    # Could not get a time for mandatory attendees
                    return redirect('/session/sessionPage/'+sessionID)
            else:
                # Get a day and time that is free for all
                # Require a minimum of 1 hour free time
                for day in availTimes.keys():
                    found = False
                    for time in availTimes[day]:
                        if timeHandler.isHourOrLonger(time):
                            chosenTime = time.split("-")[0]
                            chosenDay = day
                            found = True
                            break
                    if found:
                        break

                if chosenTime == None:
                    # There is no common time of at leat an hour
                    return redirect('/session/sessionPage/'+sessionID)

            # Initalize list of all attendees
            attendees = mandatoryAttendees

            # Iterate through non-mandatory attendees and repeat the process
            # as long as a common time greater than 1 hour still exists
            for user in sessionUsers:
                if user["id_id"] not in mandatoryAttendees:
                    availability = json.loads(user["availability"])
                    if availTimes == None:
                        temporaryTimes = availability
                    else:
                        temporaryTimes = timeHandler.timeOverlap(availTimes, availability)
                    if temporaryTimes != None:
                        for day in temporaryTimes.keys():
                            found = False
                            for time in temporaryTimes[day]:
                                if timeHandler.isHourOrLonger(time):
                                    availTimes = temporaryTimes
                                    chosenTime = time.split("-")[0]
                                    chosenDay = day
                                    attendees.append(user["id_id"])
                                    preferences = json.loads(user["preferences"])
                                    cuisinePref.append(preferences["cuisine"])
                                    foodTypePref.append(preferences["foodtype"])
                                    pricePref.append(preferences["price"])
                                    found = True
                                    break
                            if found:
                                break

            # Get datetime for right day

            weekDays = ["Sunday", "Monday", "Tuesday", "Wednesday",
                        "Thursday", "Friday", "Saturday"]
            # Chosen day code
            dayCode = weekDays.index(chosenDay)
            # Current day code (0=Sunday, 6=Saturday)
            currentDay = int(firstDay.strftime("%w"))
            timeDelta = datetime.timedelta(days=(dayCode-currentDay+7)%7)

            chosenDay = firstDay + timeDelta

            # Get OAuth data for all attending members
            attendingMembers = UserSocialAuth.objects.filter(user_id__in=attendees).values()

            # For each type of preference get most common
            preferences = getCommonPreferences(cuisinePref, foodTypePref, pricePref)

            # Get restaurant with all available data
            restaurant = getRestaurant(location, chosenTime, (int(chosenDay.strftime("%w"))+6)%7, preferences)

            if restaurant == None:
                # Could not find a suitable restaurant
                return redirect('/session/sessionPage/'+sessionID)

            # Add the event to all calendars
            makeCalendarEvents(attendingMembers, chosenDay, chosenTime, restaurant)

            # commented out for testing/demo purposes
            # session.delete()
            # return redirect('/')
            return redirect('/session/sessionPage/'+sessionID)
    return redirect('/')

def getCalendarAvailability(request, startDate):
    """
    Get free time availability for one week starting from the start date
    by parsing google calendar events for that week
    """
    context = {}
    if request.user.is_authenticated:

        # Get user credentials
        pk = request.user.pk
        auth = UserSocialAuth.objects.filter(user_id = pk)
        authvals = auth.values()
        token = authvals[0]["extra_data"]["access_token"]
        refresh = authvals[0]["extra_data"]["refresh_token"]

        # Build Google credentials
        creds = Credentials(token, refresh_token=refresh,
                 token_uri=settings.TOKEN_URI,
                 client_id=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
                 client_secret=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
                 scopes=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE)

        if creds.expired:
            creds.refresh(Request())

        # Build calendar service
        service = build("calendar", "v3", credentials = creds)

        offset = timeHandler.getTimezoneOffet()
        timeDelta = datetime.timedelta(days = 1)

        eventlst = []

        # For each day of the week, get all events from 8 am to 10 pm
        for i in range(7):
            start = str(startDate.date()) + 'T08:00:00' + offset
            end = str(startDate.date()) + 'T22:00:00' + offset
            events_result = service.events().list(calendarId='primary',
                                            timeMin=start, timeMax=end,
                                            singleEvents=True,
                                            orderBy='startTime').execute()

            events = events_result.get('items', [])

            if not events:
                pass
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                eventlst.append((start, end))

            startDate += timeDelta

        # Parse event times to get free time
        parsedTimes = timeHandler.parseEventTimes(eventlst)
        return parsedTimes

def makeCalendarEvents(attendees, chosenDay, chosenTime, restaurant):
    """
    Given a list of attendees, the chosen date and time, and the restaurant,
    add an event to all attendees' google calendars
    """

    offset = timeHandler.getTimezoneOffet()

    hour1, mins1 = chosenTime.split(":")
    endTime = str(int(hour1)+1).zfill(2) + ":" + mins1
    day = chosenDay.strftime("%Y-%m-%d")

    # Make the start and end times in full format
    start = day + "T"+chosenTime+":00"+offset
    end  = day + "T"+endTime+":00"+offset

    # Build the event details
    event = {
        "summary": "Meeting at: " + restaurant[0],
        "description": "When2Eat Meeting",
        "location": restaurant[1],
        "start": {
            "dateTime": start,
        },
        "end": {
            "dateTime": end
        },
    }

    # Add the events to all calendars
    for person in attendees:
        token = person["extra_data"]["access_token"]
        refresh = person["extra_data"]["refresh_token"]

        # Build google credentials
        creds = Credentials(token, refresh_token=refresh,
                 token_uri=settings.TOKEN_URI,
                 client_id=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
                 client_secret=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
                 scopes=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE)

        if creds.expired:
            creds.refresh(Request())

        # Build calendar service and Add event
        service = build("calendar", "v3", credentials = creds)
        service.events().insert(calendarId='primary', body=event).execute()


def getRestaurant(city, time, day, preferences):
    """
    Given the city, time, day and most popular preferences for the session,
    find a suitable restaurant.
    """

    url = "https://api.yelp.com/v3/businesses/"
    headers = {
        'Authorization': "Bearer " + settings.YELP_TOKEN
    }

    categories = ["restaurant", preferences["cuisine"]]
    if preferences["foodtype"] not in categories: #Avoid duplicate categories
        categories.append(preferences["foodtype"])

    params = {"location": city,
              "limit": "50", #Max amount to retrieve
              "categories": categories}

    if preferences["price"] != "All":
        params["price"] = preferences["price"]
    else:
        params["price"] = "1,2,3" #All prices

    #Remove ':' from time to match yelp return values
    time = time[:2] + time[3:]

    restaurantList = []
    #Get 200 matching restaurants
    for i in range(0, 201, 50):

        params["offset"] = str(i) #Start location for yelp search

        response = requests.request("GET", url+"search", headers=headers, params=params)
        data = json.loads(response.text)
        for restaurant in data["businesses"]:
            restaurantList.append(restaurant["id"])

    # For each found restaurant, check if they are open at the right time
    # When one is found, return its name and location
    for id in restaurantList:
        response = requests.request("GET", url+id, headers=headers)
        data = json.loads(response.text)
        hours = data["hours"][0]["open"]
        for opening in hours:
            if opening["day"] == day:
                if opening["start"] <= time:
                    name = data["name"]
                    location = ", ".join(data["location"]["display_address"])
                    return (name, location)
    return None


def getCommonPreferences(cuisine, foodtype, price):
    """
    Given a list of cuisine, food, and price preferences, find the
    most common preference in each category. If there is a tie, pick
    the first one.
    """
    cuisineCount = Counter(cuisine)
    foodtypeCount = Counter(foodtype)
    priceCount = Counter(price)
    return {"cuisine": cuisineCount.most_common(1)[0][0],
            "foodtype": foodtypeCount.most_common(1)[0][0],
            "price": priceCount.most_common(1)[0][0]}
