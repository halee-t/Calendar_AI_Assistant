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

limit1 = datetime.strptime("00:00:00", "%H:%M:%S").time()  # to avoid (-) times
limit2 = datetime.strptime("23:59:59", "%H:%M:%S").time()

# define context for chatGPT
day_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

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
                "original_date": {
                    "type": "string",
                    "format": "date",
                    "example": "2023-07-23",
                    "description": "It is the date the original event is scheduled for. Date must be in YYYY-MM-DD",
                },
                "original_time": {
                    "type": "string",
                    "description": "It is the time of the original event the user would like to edit. Time must be in %H:%M:%S format.",
                },
                "original_name": {
                    "type": "string",
                    "description": "The name of the event they would like to edit",
                },
                "new_date": {
                    "type": "string",
                    "format": "date",
                    "example": "2023-07-23",
                    "description": "It is the date the original event is scheduled for. Date must be in YYYY-MM-DD",
                },
                "new_time": {
                    "type": "string",
                    "description": "It is the time of the original event the user would like to edit. Time must be in %H:%M:%S format.",
                },
                "new_name": {
                    "type": "string",
                    "description": "The name of the event they would like to edit",
                }
            },
            "required": ["original_date", "original_time", "original_name"],
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

messages = [{"role": "system",
             "content": f"""You are an expert in adding events to the user's Google Calendar. You need to ask the user for the name of the event, event date and event time. You need to remember that today's date is {date.today()} and day is {day_list[date.today().weekday()]}.

        Instructions: 
        - Don't make assumptions about what values to plug into functions, if the user does not provide any of the required parameters then you must need to ask for clarification.
        - If a user request is ambiguous, then also you need to ask for clarification.
        - If a user didn't specify "ante meridiem (AM)" or "post meridiem (PM)" while providing the time, then you must have to ask for clarification. If the user didn't provide day, month, and year while giving the time then you must have to ask for clarification.
        - If a user asks to check availability of a time, you must ask for the date and time they would like to check
        - If there is a number and AM/PM anywhere in the user input, assume they are together and base the time off that
        - If a user gives you a date, format it in YYYY-MM-DD. If they don't give you a year, assume it is for 2023
        - When telling the user what details they need to provide to edit an event, make sure to tell them they need to provide each of the name, time, and date
        - You need to ask the user if they would like to edit the date, name, or time of an event when editing events. They do not need to edit each, but you need to collect the information of what they do want to edit.
        - Editing an event requires at least a new name, new date, or new time
        - When deleting events, convert time to %H:%M:%S
        - Make sure the arguments you give the functions is not empty
        - Once you pass an argument to a function, empty it so that the user can prompt you to do something with another event
        - Follow the naming conventions from the function definitions strictly
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


class APISetup:
    def __init__(self, master):
        # Create a button to submit API key
        self.submit_but = Button(master, text="Submit", command=self.submit)
        self.submit_but.grid(row=0, column=3, padx=10)

        self.myLabel = Label(master, text="Enter your API key.")
        self.myLabel.grid(row=0, column=0, padx=10)

        # Create an input box for the user to enter their key, make it hidden.
        self.api_entry = Entry(master, width=30, show="*")
        self.api_entry.grid(row=0, column=2, pady=20)

        # api key validity label
        self.myLabel4 = Label(master, text="")
        self.myLabel4.grid(row=2, column=2)

        # bind the enter key to the submit button
        self.api_entry.bind("<Return>", self.submit)

    def submit(self, event=None):
        global api_key
        api_key_entry = self.api_entry.get()
        url = "https://api.openai.com/v1/engines"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key_entry}",
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:  # api key is valid
            self.login()
            api_key = api_key_entry
            self.myLabel4.config(text="Valid API Key Entered")
        else:
            self.myLabel4.config(text="Invalid API Key Entered")

    def login(self):
        global creds, service
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            service = build('calendar', 'v3', credentials=creds)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
                service = build('calendar', 'v3', credentials=creds)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())


class Messaging:
    def __init__(self, master):
        self.send_but = Button(master, text="Send", command=self.send)
        self.send_but.grid(row=10, column=3, padx=10)

        self.myLabel2 = Label(master, text="Input:")
        self.myLabel2.grid(row=10, column=0, padx=10)

        # Create an input box for the user to send a message to the prompt.
        self.prompt_entry = Entry(master, width=30)
        self.prompt_entry.grid(row=10, column=2, pady=10)

        # Creating a label widget for the AI output
        self.myLabel3 = Label(master, text="Output:")
        self.myLabel3.grid(row=20, column=0, padx=10)

        # Create an output box for the ChatGPT output
        self.prompt_output = Text(master, width=80)
        self.prompt_output.grid(row=20, column=2, pady=10)

        # bind the entry key to the send button
        self.prompt_entry.bind("<Return>", self.send)

    def send(self, event=None):
        global api_key, messages, GPT_MODEL
        if api_key != 'x':
            messages.append({"role": "user", "content": self.prompt_entry.get()})
            self.prompt_entry.delete(0, END)
            self.prompt_output.delete(1.0, END)

            # calling chat_completion_request to call ChatGPT completion endpoint
            chat_response = chat_completion_request(messages, functions=functions, function_call=None,
                                                    model=GPT_MODEL,
                                                    api_key=api_key)

            # fetch response of ChatGPT and call the function
            assistant_message = chat_response.json()["choices"][0]["message"]

            if assistant_message['content']:
                self.prompt_output.insert(END, assistant_message['content'])
                messages.append({"role": "assistant", "content": assistant_message['content']})
            else:
                # assistant message is a dictionary
                # extracts the name of the function to be called
                fn_name = assistant_message["function_call"]["name"]
                # extracts the arguments required for the function call
                arguments = assistant_message["function_call"]["arguments"]
                # retrieves the actual function that corresponds to the name
                function = globals()[fn_name]
                # uses the retrieved function  with arguments as the parameter
                result = function(arguments, service)
                self.prompt_output.insert(END, result)
        else:
            self.prompt_output.insert(END, "Please Enter API Key")


class OpenCalendar:
    def __init__(self, master):
        self.master = master
        self.open_next = Button(master, text="Go to Google Calendar", command=self.open_cal_window)
        self.open_next.grid(row=30, column=2, padx=15)

    def open_cal_window(self):
        # Configure the size and details of window2.
        window2 = Toplevel(self.master)
        window2.title('Google Calendar')
        window2.geometry('240x140')

        # Open the file location of Google Calendar app.
        def open_cal():
            webbrowser.open_new("https://calendar.google.com/calendar/u/0/r")

        # Create a button on the second window that opens up to Google Calendar.
        open_cal = Button(window2, text="Open Google Calendar", command=open_cal)
        open_cal.pack(pady=50, padx=50)

        myLabel5 = Label(window2, text="")
        myLabel5.pack(pady=20)


api_key = "x"
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    service = build('calendar', 'v3', credentials=creds)
else:
    service = None
    creds = None


def main():
    main_wind = Tk()

    api_setup = APISetup(main_wind)

    messaging_setup = Messaging(main_wind)

    calendar_window = OpenCalendar(main_wind)

    main_wind.title("Virtual Assistant")
    main_wind.geometry('1000x540')
    main_wind.mainloop()


if __name__ == "__main__":
    main()
