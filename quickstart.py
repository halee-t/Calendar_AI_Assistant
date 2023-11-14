from __future__ import print_function

import datetime
import os.path
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime

import json
import requests
from datetime import date, datetime, timedelta
from time import time
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import pytz

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


if __name__ == '__main__':
    main()

SCOPES = ['https://www.googleapis.com/auth/calendar']
creds = Credentials.from_authorized_user_file('token.json', SCOPES)
service = build('calendar', 'v3', credentials=creds)

GPT_MODEL = "gpt-3.5-turbo-0613"


limit1 = datetime.strptime("00:00:00", "%H:%M:%S").time()  # to avoid (-) times
limit2 = datetime.strptime("23:59:59", "%H:%M:%S").time()  # highest you can go


# messages - list of messages in a conversation; each message is  a dictionary with "role": value, "content": value
# functions - modify the behavior of the model (summarizatoin, translation, or other text processing tasks
# function_call - dictionary specifying which function to call
def chat_completion_request(messages, functions=None, function_call=None, model=None, api_key=None):
    # HTTP Request headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + api_key,
    }
    # dictionary to be converted to JSON and sent in the API request (functions and function_call included if needed)
    json_data = {"model": model, "messages": messages}
    if functions is not None:
        json_data.update({"functions": functions})
    if function_call is not None:
        json_data.update({"function_call": function_call})
    # HTTP POST request sent to API, response is stored in 'response'
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

# -------------- ADDING EVENTS -------------------- #

def adding_events(arguments):
    try:
        # Gather variables from user input: Date, Time, Event Name
        provided_date = str(datetime.strptime(json.loads(arguments)['date'], "%Y-%m-%d").date())
        provided_start_time = str(
            datetime.strptime(json.loads(arguments)['time'].replace("PM", "").replace("AM", "").strip(),
                              "%H:%M:%S").time())
        start_date_time = provided_date + " " + provided_start_time
        timezone = pytz.timezone('US/Eastern')
        start_date_time = timezone.localize(datetime.strptime(start_date_time, "%Y-%m-%d %H:%M:%S"))
        event_name = str(json.loads(arguments)['event_name'])
        """
        if json.loads(arguments)['description']:
            description = str(json.loads(arguments)['description'])
        else:
            description = "This event has been scheduled by your AI assistant."
        """

        # currently the time is set for 2 hours TODO: ask for an optional end time
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
                            'description': "This event has been scheduled by your AI assistant.",

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
                        return "Event (" + event_name + ") added successfully."
                    else:
                        return "I am having troubles understanding your input. Please try again"

            # If the slot is not available, check if the user wants to proceed anyways or cancel
            elif "Sorry slot is not available" in slot_checking:
                # Create a variable for proceed. It takes the user's input
                proceed = str(input(
                    "It appears you already have an event for this timeslot, would you like to proceed? yes/no: "))

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
# Almost working for editing dates, check_availabiity(arguments) causing errors
# old event isn't deleted, basically duplicates
def editing_events(arguments):
    try:
        # Get variables from user input: Current Date, Time, and Event Name
        provided_date = str(datetime.strptime(json.loads(arguments)['date'], "%Y-%m-%d").date())
        provided_time = str(datetime.strptime(json.loads(arguments)['time'].replace("PM", "").replace("AM", "").strip(),
                                              "%H:%M:%S").time())
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
                event_to_be_changed = None
                for event in events['items']:
                    try:
                        event_date = str(datetime.fromisoformat(str(event['start']['dateTime']))).replace("T", " ")
                        if event_date == str(datetime.fromisoformat(str(start_date_time))):
                            id = event['id']
                            event_to_be_changed = event
                    except:
                        pass
                if event_to_be_changed is not None:  # the event was found
                    only_date_edited = False

                    edit_name = str(input("Would you like to edit the name of the event? (yes/no) "))
                    if edit_name == "yes":
                        only_date_edited = True

                        new_name = str(input("Enter new name for event: "))
                        event_name = new_name

                    edit_date = str(input("Would you like to edit the date of the event? (yes/no) "))
                    if edit_date == "yes":
                        only_date_edited = False

                        existing_date_time = start_date_time
                        new_date = str(input("Enter new date for event: "))
                        new_date = new_date.replace("th", "").replace("nd", "").replace("st", "").replace("rd", "")
                        new_date = new_date + ' ' + str(existing_date_time.year)
                        start_date_time = datetime.strptime(new_date, "%B %d %Y")
                        start_date_time = datetime.combine(start_date_time.date(), existing_date_time.time())

                    edit_time = str(input("Would you like to edit the time of the event? (yes/no) "))
                    if edit_time == "yes":
                        only_date_edited = False

                        time_input = str(input("Enter new time for event: "))
                        new_time_parts = time_input.split()
                        time_number = new_time_parts[0]
                        am_pm = new_time_parts[1] if len(new_time_parts) > 0 else None

                        if am_pm:
                            if am_pm.lower() == "pm" and int(time_number) < 12:
                                time_number = str(int(time_number) + 12)

                        new_time = str(datetime.strptime(time_number, "%H").time())

                        new_start_time = provided_date + " " + new_time
                        new_start_time = timezone.localize(datetime.strptime(new_start_time, "%Y-%m-%d %H:%M:%S"))
                        start_date_time = new_start_time

                    end_date_time = start_date_time + timedelta(hours=2)

                    new_arguments_dictionary = {
                        'date': start_date_time.date().strftime('%Y-%m-%d'),
                        'time': start_date_time.time().strftime('%H:%M:%S')
                    }
                    new_arguments = json.dumps(new_arguments_dictionary)

                    # We have all new info, check is new slot is available
                    if check_availability(new_arguments) == "Slot is available." and not only_date_edited:
                        event_to_be_changed['start']['dateTime'] = start_date_time.strftime("%Y-%m-%dT%H:%M:%S")
                        event_to_be_changed['end']['dateTime'] = end_date_time.strftime("%Y-%m-%dT%H:%M:%S")
                        event_to_be_changed['summary'] = event_name
                        service.events().update(calendarId='primary', eventId=id, body=event_to_be_changed).execute()
                        return "Event rescheduled."
                    elif not only_date_edited:
                        # Create a variable for proceed. It takes the user's input
                        proceed = str(input(
                            "It appears you already have an event for this timeslot, would you like to proceed? yes/no: "))

                        if proceed == "yes":
                            event_to_be_changed['start']['dateTime'] = start_date_time.strftime("%Y-%m-%dT%H:%M:%S")
                            event_to_be_changed['end']['dateTime'] = end_date_time.strftime("%Y-%m-%dT%H:%M:%S")
                            event_to_be_changed['summary'] = event_name
                            service.events().update(calendarId='primary', eventId=id,
                                                    body=event_to_be_changed).execute()
                            return "Event rescheduled."

                        elif proceed == "no":
                            return "Okay! Process canceled."

                        else:
                            return "I am having troubles understanding your input. Please try again."
                    else:
                        event_to_be_changed['start']['dateTime'] = start_date_time.strftime("%Y-%m-%dT%H:%M:%S")
                        event_to_be_changed['end']['dateTime'] = end_date_time.strftime("%Y-%m-%dT%H:%M:%S")
                        event_to_be_changed['summary'] = event_name
                        service.events().update(calendarId='primary', eventId=id, body=event_to_be_changed).execute()
                        return "Event rescheduled."
                else:
                    return "No event found."
            else:
                return "I am having troubles understanding your input. Please try again"

        else:
            return "Please provide all necessary details: Date, Time, and Event Name."
    except:
        return "We are unable to edit your event, please try again."


# ----------------- DELETING EVENTS ----------------- #

def deleting_events(arguments):
    try:
        provided_date = str(datetime.strptime(json.loads(arguments)['date'], "%Y-%m-%d").date())
        provided_time = str(datetime.strptime(json.loads(arguments)['time'].replace("PM", "").replace("AM", "").strip(),
                                              "%H:%M:%S").time())
        if provided_date and provided_time:

            start_date_time = provided_date + " " + provided_time
            timezone = pytz.timezone('US/Eastern')
            start_date_time = timezone.localize(datetime.strptime(start_date_time, "%Y-%m-%d %H:%M:%S"))

            if start_date_time < datetime.now(timezone):
                return "You have entered a date/time in the past. Please enter valid date and time."
            else:
                events = service.events().list(calendarId="primary").execute()
                id = ""
                for event in events['items']:
                    try:
                        if datetime.fromisoformat(str(event['start']['dateTime'])) == datetime.fromisoformat(
                                str(start_date_time)):
                            id = event['id']
                    except:
                        pass
                if id:
                    service.events().delete(calendarId='primary', eventId=id).execute()
                    return "Event deleted successfully."
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
        provided_date = str(datetime.strptime(json.loads(arguments)['date'], "%Y-%m-%d").date())
        provided_start_time = str(
            datetime.strptime(json.loads(arguments)['time'].replace("PM", "").replace("AM", "").strip(),
                              "%H:%M:%S").time())
        start_date_time = provided_date + " " + provided_start_time
        timezone = pytz.timezone('US/Eastern')
        start_date_time = timezone.localize(datetime.strptime(start_date_time, "%Y-%m-%d %H:%M:%S"))

        # Check to make sure the date isn't in the past
        if start_date_time < datetime.now(timezone):
            return "Your date and time are in the past"
        else:
            if start_date_time.time() >= limit1 and start_date_time.time() <= limit2:
                # Set the end time to 1 hour
                end_date_time = start_date_time + timedelta(hours=1)
                events_result = service.events().list(calendarId='primary', timeMin=start_date_time.isoformat(),
                                                      timeMax=end_date_time.isoformat(),
                                                      fields='items(summary)').execute()
                events = events_result.get('items', [])

                # This is going to help you get the name of the event, without getting your email back
                if len(events) >= 2:
                    second_event_summary = events[1].get('summary', 'No summary')
                    return "Sorry slot is not available. You have " + second_event_summary + " and others, at that time."
                elif len(events) == 1:
                    return "Sorry slot is not available. You have " + events[0].get('summary',
                                                                                    'No summary') + " at that time."
                else:
                    return "Slot is available."
    except:
        return "We are unable to check your availability, please try again."


def add_generation(arguments):
    print(arguments)
    arguments_json = json.loads(arguments)
    for event in arguments_json['schedule']:
        print(event['event_name'])




# ------------------- FUNCTION SPECIFICATION --------------------- #



