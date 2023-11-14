import tkinter as tk
from tkinter import *
from tkinter import filedialog
import webbrowser
from quickstart import *

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime


main_wind = Tk()

main_wind.title("Virtual Assistant")
main_wind.geometry('1000x540')
# Change the default bg from white to black
# window.configure(bg='#333333')

#Creating a label widget for the API key
myLabel = Label(main_wind, text="Enter your API key.")
myLabel.grid(row=0, column=0, padx=10)

#Create an input box for the user to enter their key, make it hidden.
api_entry = Entry(main_wind, width=30, show="*")
api_entry.grid(row=0, column=2, pady=20)

api_key = "x"

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


#This is what will happen when the submit button is pressed.
#-----------I want it to go to the next input box after the API is put in, will fix this later.
def submit():
    if api_entry.get() == api_key:
        myLabel4 = Label(main_wind, text="Successfully logged in.")
        myLabel4.grid(row=2, column=2)
    else:
        myLabel3 = Label(main_wind, text="Invalid API key")
        myLabel3.grid(row=2, column=2)


#Create a button to submit API key
submit_but = Button(main_wind, text="Submit",  command=submit)
submit_but.grid(row=0, column=3, padx=10)


#Creating a label widget for the AI prompt.
myLabel2 = Label(main_wind, text="Input:")
myLabel2.grid(row=10, column=0, padx=10)


#Create an input box for the user to send a message to the prompt.
prompt_entry = Entry(main_wind, width=30)
prompt_entry.grid(row=10, column=2, pady=10)


# Creating a label widget for the AI output
myLabel3 = Label(main_wind, text="Output:")
myLabel3.grid(row=20, column=0, padx=10)

prompt_output = Text(main_wind, width=80)
prompt_output.grid(row=20, column=2, pady=10)



# define context for chatGPT
day_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

messages = [{"role": "system",
                 "content": f"""You are an expert in adding events to the user's Google Calendar. You need to ask the user for the name of the event, event date and event time. You need to remember that today's date is {date.today()} and day is {day_list[date.today().weekday()]}.

    Instructions: 
    - Don't make assumptions about what values to plug into functions, if the user does not provide any of the required parameters then you must need to ask for clarification.
    - If a user request is ambiguous, then also you need to ask for clarification.
    - If a user didn't specify "ante meridiem (AM)" or "post meridiem (PM)" while providing the time, then you must have to ask for clarification. If the user didn't provide day, month, and year while giving the time then you must have to ask for clarification.
    - If a user asks to check availability of a time, you must ask for the date and time they would like to check
    - If there is a number and AM/PM anywhere in the user input, assume they are together and base the time off that
    - If a user gives you a date, format it in YYYY-MM-DD. If they don't give you a year, assume it is for 2023
    - After you collect the necessary information for editing events, do not ask any further questions or for further details
    - When deleting events, convert time to %H:%M:%S
    - Make sure the arguments you give the functions is not empty
    - Once you pass an argument to a function, empty it so that the user can prompt you to do something with another event
    - EditingEventInfoCollected
    For generating a schedule:
    - First ask what tasks they would like the day to be scheduled around, and if any have to be at a specific time. Do not ask about specific times beyond the initial inquiry
    - Remember the adjustments that the user is making to the suggested schedule in the active run.
    - If the user does not specify when they would like to start and end their day, please ask and adjust accordingly.
    - If the user would like to study, include 15 minute breaks between all consecutive study periods
    - If the user specifies a time they have an event at, that event MUST start at that time always.
    - If the user mentions breakfast, it must start between 7AM and 11AM unless otherwise specified.
    - If the user mentions lunch, it must start between 12PM and 3PM unless otherwise specified.
    - If the user mentions dinner or making dinner, it must start between 5PM and 7PM unless otherwise specified. Dinner also does not have to be the last event of the day
    - Fill the entire day the user wants with tasks; include breaks
    - Do not ask for how long tasks should take. If the user does not specify, come up with suggested times and build the schedule around them
    - After generating the schedule, ask if the user would like to make any adjustments and if they would like to add the schedule to their calendar
    - If the user wants to add a schedule to their calendar, you need to ask what day

    Make sure to follow the instructions carefully while processing the request. 
    """}]

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
                    "example": "2023-07-23",
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
                    "example": "2023-07-23",
                    "description": "It is the date the original event is scheduled for. Date must be in YYYY-MM-DD",
                },
                "time": {
                    "type": "string",
                    "description": "It is the time of the original event the user would like to edit. Time must be in %H:%M:%S format.",
                },
                "event_name": {
                    "type": "string",
                    "description": "The name of the event they would like to edit",
                }
            },
            "required": ["date", "time", "event_name"],
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
                    "example": "2023-07-23",
                    "description": "Date, on which user has an event and wants to delete it. The date must be in the format of YYYY-MM-DD.",
                },
                "time": {
                    "type": "string",
                    "description": "time, on which user has an event and wants to delete it. Time must be in %H:%M:%S format.",
                },
            },
            "required": ["date", "time"],
        },
    },
    {
        # For CHECKING AVAILABILITY
        "name": "check_availability",
        "description": "When user wants to check if time slot is available or not, then this function should be called.",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "format": "date",
                    "example": "2023-07-23",
                    "description": "Date, when the user wants to add an event. The date must be in the format of YYYY-MM-DD.",
                },
                "time": {
                    "type": "string",
                    "example": "20:12:45",
                    "description": "time, on which user wants to add an event on a specified date. Time must be in %H:%M:%S format.",
                }
            },
            "required": ["date", "time"],
        },
    },
    {
        "name": "add_generation",
        "description": "Add a generated event to the user's calendar",
        "parameters": {
            "type": "object",
            "properties": {
                "schedule": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "event_name": {
                                "type": "string",
                                "description": "Name of the generated event"
                            },
                            "start_time": {
                                "type": "string",
                                "description": "Start time of the generated event (in %H:%M:%S format)"
                            },
                            "end_time": {
                                "type": "string",
                                "description": "End time of the generated event (in %H:%M:%S format)"
                            }
                        },
                        "required": ["event_name", "start_time"]
                    },
                    "description": "List of generated events to add to the calendar"
                },
                "user_date": {
                    "type": "string",
                    "format": "date",
                    "example": "2023-07-23",
                    "description": "Date on which to add the generated events (YYYY-MM-DD)"
                }
            },
            "required": ["schedule", "user_date"]
        }
    }

]

# This defines the send button, and what happens when you press it.
def send():
    global messages

    messages.append({"role": "user", "content": prompt_entry.get()})
    prompt_entry.delete(0, END)
    prompt_output.delete(1.0, END)

    # calling chat_completion_request to call ChatGPT completion endpoint
    chat_response = chat_completion_request(messages, functions=functions, function_call=None, model=GPT_MODEL,
                                            api_key=api_key)

    # fetch response of ChatGPT and call the function
    assistant_message = chat_response.json()["choices"][0]["message"]

    if assistant_message['content']:
        prompt_output.insert(END, assistant_message['content'])
        messages.append({"role": "assistant", "content": assistant_message['content']})
    else:
        # assistant message is a dictionary
        # extracts the name of the function to be called
        fn_name = assistant_message["function_call"]["name"]
        # extracts the arguments required for the function call
        arguments = assistant_message["function_call"]["arguments"]
        # retrieves the actual function that corresponds to the name
        function = globals()[fn_name]
        # uses the retrieved function with arguments as the parameter
        result = function(arguments, service)
        prompt_output.insert(END, result)



creds = Credentials.from_authorized_user_file('token.json', SCOPES)
service = build('calendar', 'v3', credentials=creds)

GPT_MODEL = "gpt-3.5-turbo-0613"

limit1 = datetime.strptime("00:00:00", "%H:%M:%S").time()  # to avoid (-) times
limit2 = datetime.strptime("23:59:59", "%H:%M:%S").time()





#Create a button to send the message from the prompt.
send_but = Button(main_wind, text="Send",  command=send)
send_but.grid(row=10, column=3, padx=10)



#Define the open command and create a second window. 
def open():
    # Configure the sixe and details of window2.
    window2 = Toplevel(main_wind)
    window2.title('Google Calendar')
    window2.geometry('240x140')

    #Open the file location of Google Calender app. 
    def open_cal():
        webbrowser.open_new("https://calendar.google.com/calendar/u/0/r")

    #Create a button on the second window that opens up to Google Calendar.
    open_cal = Button(window2, text="Open Google Calendar", command=open_cal)
    open_cal.pack(pady=50, padx=50)

    myLabel5 = Label(window2, text="")
    myLabel5.pack(pady=20)
    


#Create a button to open second window.
open_next = Button(main_wind, text="Go to Google Calendar", command=open)
open_next.grid(row=30, column=2, padx=15)
 

#---------- Not sure if I need this line: main_wind.mainloop()
main_wind.mainloop()