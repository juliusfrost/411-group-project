def getForms(isHost):
    """
    Get appropriate forms for host and guests.
    """
    if isHost:
        return getHostFroms() + '<br>' + getRestaurantForms()
    return getRestaurantForms()

def getHostFroms():
    """
    Forms for name, date, and location. Only to be set by host.
    """
    return '''
    <div class="form-group"><label class="text-black-50 d-lg-flex justify-content-lg-start">Session Name</label><input class="form-control" type="text" id="name" name="name"></div>
    <div class="form-group"><label class="text-black-50 d-lg-flex justify-content-lg-start">Start Date</label><input class="form-control" type="date" id="date" name="date"></div>
    <div class="form-group"><label class="text-black-50 d-lg-flex justify-content-lg-start">Location (City)</label><input class="form-control" type="text" id="Location" name="location"required></div>
    '''

def getRestaurantForms():
    """
    Forms for cuisine, food type, and price range.
    """
    return '''
    <label class="text-black-50 d-lg-flex justify-content-lg-start">Restaurant Options:</label><br>
    <div class="form-group">
    <label class="text-black-50 d-lg-flex justify-content-lg-start">Cuisine (optional):</label>
    <select class="form-control" id="cuisine" name="cuisine">
    <option value="All">No preference</option>
    <option value="italian">Italian</option>
    <option value="french">French</option>
    <option value="chinese">Chinese</option>
    <option value="japanese">Japanese</option>
    <option value="spanish">Spanish</option>
    </select></div>
    <div class="form-group">
    <label class="text-black-50 d-lg-flex justify-content-lg-start">Food Type (optional):</label>
    <select class="form-control" id="foodtype" name="foodtype">
    <option value="All">No preference</option>
    <option value="seafood">Seafood</option>
    <option value="pizza">Pizza</option>
    <option value="mediterranean">Mediterranean</option>
    <option value="sushi">Sushi</option>
    <option value="steak">Steak</option>
    </select></div>
    <div class="form-group">
    <label class="text-black-50 d-lg-flex justify-content-lg-start">Price (optional):</label>
    <select class="form-control" id="price" name="price">
    <option value="All">No preference</option>
    <option value="1">Low</option>
    <option value="2">Medium</option>
    <option value="3">High</option>
    </select></div>
    '''

def getCreateOrJoinButton(create):
    """
    Button to either create or join a session.
    """
    if create:
        return '''
               <button class="btn btn-primary btn-lg" type="submit"
               onclick="this.form.action='createSession/';">Create Session</button>
               '''
    else:
        return '''
               <button class="btn btn-primary btn-lg" type="submit"
               onclick="this.form.action='joinSession/';">Join Session</button>
               '''

def getLockOrSolveButton(lock):
    """
    Button to either lock or solve the session.
    """
    if lock:
        return '''
               <button class="btn btn-primary" type="submit"
               onclick="this.form.action='solveSession/';">Solve</button>
               '''
    else:
        return '''
               <button class="btn btn-primary" type="submit"
               onclick="this.form.action='lockSession/';">Lock</button>
               '''
