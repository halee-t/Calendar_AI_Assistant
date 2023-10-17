from __future__ import print_function

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']


def main():

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    ### TODO: LOGIN CODE HERE
    # Idea: If we delete the token.json before pushing, everytime someone else runs the code they will have to log in. That could be our security
    # This way, it is a one-time login

   
if __name__ == '__main__':
    main()


import json
import requests
from datetime import date, datetime, timedelta
from time import time
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import pytz

SCOPES = ['https://www.googleapis.com/auth/calendar']
creds = Credentials.from_authorized_user_file('token.json', SCOPES)
service = build('calendar', 'v3', credentials=creds)

GPT_MODEL = "gpt-3.5-turbo-0613"

# YOUR API KEY IS GOING HERE. REMEMBER TO REMOVE
openai_api_key = "x"

def chat_completion_request(messages, functions=None, function_call=None, model=GPT_MODEL):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + openai_api_key,
    }
    json_data = {"model": model, "messages": messages}
    if functions is not None:
        json_data.update({"functions": functions})
    if function_call is not None:
        json_data.update({"function_call": function_call})
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e



### IT'S ON MILITARY TIME!!!! So when I do 1PM, it takes away the PM and thinks its 1 am
### I noticed that if I do 7 PM it does 7 PM, but 7PM does 7 AM
# TODO: The time can still be iffy. Continue to work on tweaking this
limit1 = datetime.strptime("00:00:00", "%H:%M:%S").time()       # to avoid (-) times
limit2 = datetime.strptime("23:59:59", "%H:%M:%S").time()       # highest you can go

# -------------- ADDING EVENTS -------------------- #

def adding_events(arguments):
    try:

        # Gather variables from user input: Date, Time, Event Name
        provided_date =  str(datetime.strptime(json.loads(arguments)['date'], "%Y-%m-%d").date())
        provided_start_time = str(datetime.strptime(json.loads(arguments)['time'].replace("PM","").replace("AM","").strip(), "%H:%M:%S").time())
        start_date_time = provided_date + " " + provided_start_time
        timezone = pytz.timezone('US/Eastern')
        start_date_time = timezone.localize(datetime.strptime(start_date_time, "%Y-%m-%d %H:%M:%S"))
        event_name = str(json.loads(arguments)['event_name'])

        #currently the time is set for 2 hours TODO: ask for an optional end time
        end_date_time = start_date_time + timedelta(hours=2)
        
        # If the user has provided the Date, Time, and Event Name, you may proceed
        if provided_date and provided_start_time and event_name:

            # Check to see if the desired time slot is available
            slot_checking = check_availability(arguments)

            # If the slot is available, proceed
            if slot_checking == "Slot is available.":  

                # Make sure that the time the user entered isn't in the past
                if start_date_time < datetime.now(timezone):
                    return "The date that you have entered is in the past. Please enter a valid date and time."
                else:
                    # Make sure we are in a valid time range
                    if start_date_time.time() >= limit1 and start_date_time.time() <= limit2:
                        # This is the information needed for Google Calendar. Summary is the event name, location will be set to blank,
                        # description is to let the user know that this event was added through our program
                        event = {
                            'summary': event_name,
                            'location': "",
                            'description': "This event has been scheduled by your AI Assistant.",
                            
                            'start': {
                                'dateTime': start_date_time.strftime("%Y-%m-%dT%H:%M:%S"),
                                'timeZone': 'US/Eastern',
                            },
                            'end': {
                                'dateTime': end_date_time.strftime("%Y-%m-%dT%H:%M:%S"),
                                'timeZone': 'US/Eastern',
                            },

                            # Reminders are set to go off as an email and a popup notification on the users phone
                            'reminders': {
                                'useDefault': False,
                                'overrides': [
                                    {'method': 'email', 'minutes': 24 * 60},
                                    {'method': 'popup', 'minutes': 10},
                                ],
                            },
                        }
                        service.events().insert(calendarId='primary', body=event).execute()
                        # This is just for testing purposes
                        print(chat_response.json())
                        return "Event (" + event_name + ") added successfully."
                    else:
                        return "I am having troubles understanding your input. Please try again"
                        
            # If the slot is not available, check if the user wants to proceed anyways or cancel
            elif "Sorry slot is not available" in slot_checking:
                # Create a variable for proceed. It takes the user's input
                proceed = str(input("It appears you already have an event for this timeslot, would you like to proceed? yes/no: "))
                
                if proceed == "yes":
                    ### FUTURE REFACTOR: THIS IS DUPLICATED CODE, MAYBE MAKE IT INTO A METHOD
                    if start_date_time < datetime.now(timezone):
                        return "The date that you have entered is in the past. Please enter a valid date and time."
                    else:
                        ### Make sure we are in a valid time range
                        if start_date_time.time() >= limit1 and start_date_time.time() <= limit2:
                            event = {
                                # ADDED THIS SO THE NAME SHOWS IN CALENDAR
                                'summary': event_name,
                                'location': "",
                                'description': "This event has been scheduled by your AI Assistant.",
                                
                                'start': {
                                    'dateTime': start_date_time.strftime("%Y-%m-%dT%H:%M:%S"),
                                    'timeZone': 'US/Eastern',
                                },
                                'end': {
                                    'dateTime': end_date_time.strftime("%Y-%m-%dT%H:%M:%S"),
                                    'timeZone': 'US/Eastern',
                                },

                                ## This is where the REMINDER section is
                                'reminders': {
                                    'useDefault': False,
                                    'overrides': [
                                        {'method': 'email', 'minutes': 24 * 60},
                                        {'method': 'popup', 'minutes': 10},
                                    ],
                                },
                            }
                            service.events().insert(calendarId='primary', body=event).execute()
                            # This is just for testing purposes
                            print(chat_response.json())
                            return "Great! Event (" + event_name + ") added successfully."
                        else:
                            return "I am having troubles understanding your input. Please try again"
                        
                elif proceed == "no":
                    return "Okay! Process canceled."
                
                else:
                    return "I am having troubles understanding your input. Please try again."

            # Something went wrong, return the error message
            else: 
                return slot_checking
        
        # If the user has not provided all required information (Date, Time, Name of Event), ask them to
        else:
            return "Please provide all necessary details: Name of event, date, and time"
        
    except:
        return "We are facing an error while adding your event. Please try again."
    

# ------------------- EDITING EVENTS ------------------- #
# Doesn't work yet :(
def editing_events(arguments):
    try:
        # Get variables from user input: Current Date, Time, and Event Name
        provided_date =  str(datetime.strptime(json.loads(arguments)['date'], "%Y-%m-%d").date())
        provided_time = str(datetime.strptime(json.loads(arguments)['time'].replace("PM","").replace("AM","").strip(), "%H:%M:%S").time())
        start_date_time = provided_date + " " + provided_time
        timezone = pytz.timezone('US/Eastern')
        start_date_time = timezone.localize(datetime.strptime(start_date_time, "%Y-%m-%d %H:%M:%S"))
        event_name = str(json.loads(arguments)['event_name'])
        
        # Check to see if the user has provided all necessary information
        if provided_date and provided_time and event_name:
            # Make sure date isn't in the past
            if start_date_time < datetime.now(timezone):
                return "The time you have entered is in the past. Please enter valid date and time."
            
            # Got all the new info, now we can edit
            if start_date_time.time() >= limit1 and start_date_time.time() <= limit2:
                end_date_time = start_date_time + timedelta(hours=2)
                events = service.events().list(calendarId="primary").execute()
                id = ""
                final_event = None
                for event in events['items']:
                    id = event['id']
                    final_event = event
                if final_event: #the event was found

                    edit_name = str(input("Would you like to edit the name of the event? (yes/no) "))
                    if edit_name == "yes":
                        new_name = str(input("Enter new name for event: "))
                        event_name = new_name

                    edit_date = str(input("Would you like to edit the date of the event? (yes/no) "))
                    if edit_date == "yes":
                        new_date = str(input("Enter new date for event: "))
                        provided_date = new_date

                    edit_time = str(input("Would you like to edit the time of the event? (yes/no) "))
                    # THIS IS WHERE ERRORS OCCUR
                    if edit_time == "yes": 
                        holder = str(input("Enter new time for event: "))
                        new_provided_time = str(datetime.strptime(json.loads(arguments)['new_time'].replace("PM","").replace("AM","").strip(), "%H:%M:%S").time())
                        print(new_provided_time)
                        new_start_time = provided_date + " " + new_provided_time
                        new_start_time = timezone.localize(datetime.strptime(new_start_time, "%Y-%m-%d %H:%M:%S"))
                        start_date_time = new_start_time

                    # We have all new info, check is new slot is available
                    if check_availability(arguments) == "Slot is available.":
                        final_event['start']['dateTime'] = start_date_time.strftime("%Y-%m-%dT%H:%M:%S")
                        final_event['end']['dateTime'] = end_date_time.strftime("%Y-%m-%dT%H:%M:%S")
                        service.events().update(calendarId='primary', eventId=id, body=final_event).execute()
                        return "Event rescheduled."
                    else:
                        # Create a variable for proceed. It takes the user's input
                        proceed = str(input("It appears you already have an event for this timeslot, would you like to proceed? yes/no: "))
                        
                        if proceed == "yes":
                            final_event['start']['dateTime'] = start_date_time.strftime("%Y-%m-%dT%H:%M:%S")
                            final_event['end']['dateTime'] = end_date_time.strftime("%Y-%m-%dT%H:%M:%S")
                            service.events().update(calendarId='primary', eventId=id, body=final_event).execute()
                            return "Event rescheduled."
                                
                        elif proceed == "no":
                            return "Okay! Process canceled."
                        
                        else:
                            return "I am having troubles understanding your input. Please try again."
                else:
                    return "No event found."
            else:
                return "I am having troubles understanding your input. Please try again"
                
           

        else: 
            return "Please provide all necessary details: Date, Time, and Event Name."
    except:
        return "We are unable to edit your event, please try again."


# ----------------- DELETING EVENTS ----------------- #

# TODO: Not working :(
def deleting_events(arguments):
    try:
        provided_date = str(datetime.strptime(json.loads(arguments)['date'], "%Y-%m-%d").date())
        provided_time = str(datetime.strptime(json.loads(arguments)['time'].replace("PM","").replace("AM","").strip(), "%H:%M:%S").time())
        start_date_time = provided_date + " " + provided_time
        timezone = pytz.timezone('US/Eastern')
        start_date_time = timezone.localize(datetime.strptime(start_date_time, "%Y-%m-%d %H:%M:%S"))
        event_name = str(json.loads(arguments)['event_name'])

        if provided_date and provided_time and event_name:

            if start_date_time < datetime.now(timezone):
                return "You have entered a date/time in the past. Please enter valid date and time."
            
            else:
                events = service.events().list(calendarId="primary").execute()
                id = ""
                for event in events['items']:
                    if datetime.fromisoformat(str(event['start']['dateTime'])) == datetime.fromisoformat(str(start_date_time)):
                        id = event['id']
                if id:
                    service.events().delete(calendarId='primary', eventId=id).execute()
                    return "Event (" + event_name + ") deleted successfully."
                else:
                    return "No event found"
        else:
            return "Please provide all necessary details: Start date, Start time and Event name."
    except:
        return "We are unable to delete your event, please try again."
    

# ---------------- CHECK AVAILABILITY ---------------- #

def check_availability(arguments):
    try:
        # Declare variables for Date, and Time
        provided_date =  str(datetime.strptime(json.loads(arguments)['date'], "%Y-%m-%d").date())
        provided_start_time = str(datetime.strptime(json.loads(arguments)['time'].replace("PM","").replace("AM","").strip(), "%H:%M:%S").time())
        start_date_time = provided_date + " " + provided_start_time
        timezone = pytz.timezone('US/Eastern')
        start_date_time = timezone.localize(datetime.strptime(start_date_time, "%Y-%m-%d %H:%M:%S"))

        # Check to make sure the date isn't in the past
        if start_date_time < datetime.now(timezone):
            return "Please enter valid date and time."
        else:
            if start_date_time.time() >= limit1 and start_date_time.time() <= limit2:
                # Set the end time to 1 hour
                end_date_time = start_date_time + timedelta(hours=1)
                events_result = service.events().list(calendarId='primary', timeMin=start_date_time.isoformat(), timeMax=end_date_time.isoformat(), fields='items(summary)').execute()
                events = events_result.get('items', [])

                # This is going to help you get the name of the event, without getting your email back
                if len(events) >= 2:
                    second_event_summary = events[1].get('summary', 'No summary')

                # If an event was found, let the user know
                if events_result['items']:
                    return "Sorry slot is not available. You have " + second_event_summary + " at that time."
                # If no event was found, let the user know
                else:
                    return "Slot is available."
    except:
        return "We are unable to check your availability, please try again."


# ------------------- FUNCTION SPECIFICATION --------------------- #
functions = [
    {
        # For ADDING EVENTS
        "name": "adding_events",
        "description": "When user want to add an event, then this function should be called.",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "format": "date",
                    "example":"2023-07-23",
                    "description": "Date, when the user wants to add an event. The date must be in the format of YYYY-MM-DD.",
                },
                "time": {
                    "type": "string",
                    "example": "20:12:45", 
                    "description": "time, on which user wants to add an event on a specified date. Time must be in %H:%M:%S format.",
                },
                "event_name": {
                    "type": "string",
                    "description": "Name of the event that the user is trying to add",
                }
            },

            "required": ["date", "time", "event_name"],
        },
    },
    {
        # For EDITING EVENTS
        "name": "editing_events",
        "description": "When user wants to edit an event, then this function should be called.",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "format": "date",
                    "example":"2023-07-23",
                    "description": "It is the date on which the user wants to edit the event. The date must be in the format of YYYY-MM-DD.",
                },
                "time": {
                    "type": "string",
                    "description": "It is the time on which user wants to edit the event. Time must be in %H:%M:%S format.",
                },
                "new_time": {
                    "type": "string",
                    "description": "It is the time that the user enters when asked: Enter new time for event: '. Time must be in %H:%M:%S format.",
                },
                "event_name": {
                    "type": "string",
                    "description": "The name of the event they would like to edit",
                }
            },
            "required": ["date","time","event_name"],
        },
    },
    {
        # For DELETING EVENTS
        "name": "deleting_events",
        "description": "When user want to delete an event, then this function should be called.",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "format": "date",
                    "example":"2023-07-23",
                    "description": "Date, on which user has an event and wants to delete it. The date must be in the format of YYYY-MM-DD.",
                },
                "time": {
                    "type": "string",
                    "description": "time, on which user has an event and wants to delete it. Time must be in %H:%M:%S format.",
                },
                "event_name": {
                    "type": "string",
                    "description": "Name of the event that the user is trying to delete",
                }
            },
            "required": ["date","time", "event_name"],
        },
    },
    {
        #For CHECKING AVAILABILITY
        "name": "check_availability",
        "description": "When user wants to check if time slot is available or not, then this function should be called.",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "format": "date",
                    "example":"2023-07-23",
                    "description": "Date, when the user wants to add an event. The date must be in the format of YYYY-MM-DD.",
                },
                "time": {
                    "type": "string",
                    "example": "20:12:45", 
                    "description": "time, on which user wants to add an event on a specified date. Time must be in %H:%M:%S format.",
                }
            },
            "required": ["date","time"],
        },
    }]


# --------------- TESTING --------------------- # 

day_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

messages = [{"role": "system", "content": f"""You are an expert in adding events to the user's Google Calendar. You need to ask the user for the name of the event, event date and event time. You need to remember that today's date is {date.today()} and day is {day_list[date.today().weekday()]}.

Instructions: 
- Don't make assumptions about what values to plug into functions, if the user does not provide any of the required parameters then you must need to ask for clarification.
- If a user request is ambiguous, then also you need to ask for clarification.
- When a user asks for a rescheduling date or time of the current event, then you must ask for the new event details only.
- If a user didn't specify "ante meridiem (AM)" or "post meridiem (PM)" while providing the time, then you must have to ask for clarification. If the user didn't provide day, month, and year while giving the time then you must have to ask for clarification.
- Format the output as the Google Calendar API json

Make sure to follow the instructions carefully while processing the request. 
"""}]

user_input = input("Please enter your question here: (if you want to exit then write 'exit' or 'bye'.) ")

while user_input.strip().lower() != "exit" and user_input.strip().lower() != "bye":
    
    messages.append({"role": "user", "content": user_input})

    # calling chat_completion_request to call ChatGPT completion endpoint
    chat_response = chat_completion_request(
        messages, functions=functions
    )

    # fetch response of ChatGPT and call the function
    assistant_message = chat_response.json()["choices"][0]["message"]

    if assistant_message['content']:
        print("Response is: ", assistant_message['content'])
        messages.append({"role": "assistant", "content": assistant_message['content']})
    else:
        fn_name = assistant_message["function_call"]["name"]
        arguments = assistant_message["function_call"]["arguments"]
        function = locals()[fn_name]
        result = function(arguments)
        print("Response is: ", result)
       
    user_input = input("Please enter your question here: ")