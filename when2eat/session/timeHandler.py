import datetime, time

def getEndDate(startDate):
    """
    Given a start date string, return a datetime object for the start date
    and the end date. If there is no start date, make the next day the
    start date.
    """
    if startDate == "":
        startDate = datetime.datetime.today()
        timeDelta = datetime.timedelta(days = 1)
        startDate = startDate + timeDelta
    else:
        # Convert to datetime
        startDate = startDate.split('-')
        startDate = [int(i) for i in startDate]
        startDate = datetime.datetime(startDate[0], startDate[1], startDate[2])

    #Get end date 6 days away for a one-week outlook
    timeDelta = datetime.timedelta(days = 6)
    endDate = startDate + timeDelta
    return (startDate, endDate)

def parseEventTimes(events):
    """
    Given a list of ordered start and end times from Google calendar events,
    find the remaining free time for the week. Only consider times between
    8 am and 10 pm. Assume no overlapping events.
    """
    freeTime = {"Monday": ["08:00-22:00"],
                "Tuesday": ["08:00-22:00"],
                "Wednesday": ["08:00-22:00"],
                "Thursday": ["08:00-22:00"],
                "Friday": ["08:00-22:00"],
                "Saturday": ["08:00-22:00"],
                "Sunday": ["08:00-22:00"]}

    for startDate, endDate in events:
        start = datetime.datetime.strptime(startDate, "%Y-%m-%dT%H:%M:%S%z")
        end = datetime.datetime.strptime(endDate, "%Y-%m-%dT%H:%M:%S%z")
        weekday = start.strftime('%A') #Full weekday name
        freeTime[weekday] = splitTime(freeTime[weekday],
                              start.strftime('%H:%M'),
                              end.strftime('%H:%M'))
    return freeTime

def splitTime(freeTime, start, end):
    """
    Given the free time for one day, remove the time between start and
    end times.
    """
    start = boundTime(start)
    end = boundTime(end)
    latestInterval = freeTime[-1]
    endpoints = latestInterval.split("-")

    if endpoints[0] == start and endpoints[1] == end:
        # Latest time interval is the same as event
        freeTime.pop()
    elif endpoints[0] == start:
        # Latest time interval starts at same time as event
        interval = "{}-{}".format(end, endpoints[1])
        freeTime[-1] = interval
    elif endpoints[1] == end:
        # Latest time interval ends at same time as event
        interval = "{}-{}".format(endpoints[0], start)
        freeTime[-1] = interval
    else:
        # Event time falls between latest interval
        interval1 = "{}-{}".format(endpoints[0], start)
        interval2 = "{}-{}".format(end, endpoints[1])
        freeTime[-1] = interval1
        freeTime.append(interval2)
    return freeTime

def getTimeBlockAvailability(timeBlocks):
    """
    Given a list of times to be blocked in one hour intervals,
    find remaining free time for the week. Only consider times between
    8 am and 10 pm
    """
    freeTime = {"Monday": ["08:00-22:00"],
                "Tuesday": ["08:00-22:00"],
                "Wednesday": ["08:00-22:00"],
                "Thursday": ["08:00-22:00"],
                "Friday": ["08:00-22:00"],
                "Saturday": ["08:00-22:00"],
                "Sunday": ["08:00-22:00"]}

    for time in timeBlocks:
        timeSlot = time.split("-")
        freeTime[weekDay] = splitTime(freeTime[weekDay],
                                timeSlot[0],
                                timeSlot[1])

    return freeTime

def equalTime(time1, time2):
    hour1, min1 = time1.split(":")
    hour2, min2 = time2.split(":")
    return int(hour1) == int(hour2) and int(min1) == int(min2)

def greaterTime(time1, time2):
    hour1, min1 = time1.split(":")
    hour2, min2 = time2.split(":")
    return (int(hour1) > int(hour2)) or (int(hour1) == int(hour2) and int(min1) > int(min2))

def lesserTime(time1, time2):
    hour1, min1 = time1.split(":")
    hour2, min2 = time2.split(":")
    return (int(hour1) < int(hour2)) or (int(hour1) == int(hour2) and int(min1) < int(min2))

def lessEqualTime(time1, time2):
    return equalTime(time1, time2) or lesserTime(time1, time2)

def greatEqualTime(time1, time2):
    return equalTime(time1, time2) or greaterTime(time1, time2)

def boundTime(time):
    """
    Given a specific time, bound the time between 8 am and 10 pm
    """
    if time < "08:00":
        return "08:00"
    if time > "22:00":
        return "22:00"
    return time

def timeOverlap(avail1, avail2):
    """
    Given two sets of availabilities for the week, find the common time
    availabilities.
    """
    freeTime = {"Monday": [],
                "Tuesday": [],
                "Wednesday": [],
                "Thursday": [],
                "Friday": [],
                "Saturday": [],
                "Sunday": []}

    for day in freeTime.keys():
        for time1 in avail1[day]:
            for time2 in avail2[day]:
                t1start, t1end = time1.split("-")
                t2start, t2end = time2.split("-")
                if t1start == t2start and t1end == t2end:
                    #Perfectly overlapping availabilities
                    freeTime[day].append(time1)
                elif t1start <= t2start and t1end >= t2end:
                    # time1 has bigger range then time2
                    freeTime[day].append(time2)
                elif t1start >= t2start and t1end <= t2end:
                    # time2 has bigger range than time1
                    freeTime[day].append(time1)
                elif t2start > t1end:
                    # time2 is entirely after time1
                    continue
                elif t1start > t2end:
                    # time1 is entirely after time2
                    continue
                elif t1start < t2start and t1end < t2end:
                    # Partial overlap time1 starts and ends earlier
                    freeTime[day].append('{}-{}'.format(t2start, t1end))
                else:
                    # Partial overlap time2 starts and ends earlier
                    freeTime[day].append('{}-{}'.format(t1start, t2end))
    return freeTime

def isHourOrLonger(timeSlot):
    """
    Determine whether a given time slot is at least an hour long.
    """
    start, end = timeSlot.split("-")
    hour1, mins1 = start.split(":")
    hour2, mins2 = end.split(":")
    time1 = datetime.time(int(hour1), int(mins1))
    time2 = datetime.time(int(hour2), int(mins2))
    dateTime1 = datetime.datetime.combine(datetime.date.today(), time1)
    dateTime2 = datetime.datetime.combine(datetime.date.today(), time2)
    timeDifferenceMinutes = (dateTime2 - dateTime1).total_seconds() / 60
    return timeDifferenceMinutes > 60

def getTimezoneOffet():
    """
    Get the offset for the local time zone
    """
    lt = time.localtime()
    offmins = int(time.altzone / 60)
    offhours = int(offmins / 60)
    offmins -= offhours * 60
    offhours = offhours + (0 if lt.tm_isdst == 0 else 1)
    offmins = str(offmins).zfill(2)
    offhours = str(offhours).zfill(2)
    offset = '-{}:{}'.format(offhours, offmins)
    return offset
