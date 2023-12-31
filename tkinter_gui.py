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
                },
                "override_schedule_conflict": {
                    "type": "string",
                    "description": "yes or no depending on if the user wants to schedule their event even if their is an event already scheduled at the given time"
                }
            },

            "required": ["date", "time", "event_name", "override_schedule_conflict"],
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
        # For ADD GENERATION
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
                "date": {
                    "type": "string",
                    "format": "date",
                    "example": "2023-07-23",
                    "description": "Date on which to add the generated events (YYYY-MM-DD)"
                }
            },
            "required": ["schedule", "date"]
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
        - If there is an event scheduled at [the time the user provides], would you like to schedule your event anyway?"
        - When telling the user what details they need to provide to edit an event, make sure to tell them they need to provide each of the name, time, and date
        - You need to ask the user if they would like to edit the date, name, or time of an event when editing events. They do not need to edit each, but you need to collect the information of what they do want to edit.
        - Editing an event requires at least a new name, new date, or new time
        - Convert given times to %H:%M:%S
        - Make sure the arguments you give the functions is not empty
        - Once you pass an argument to a function, empty it so that the user can prompt you to do something with another event
        - Follow the naming conventions from the function definitions strictly
        For generating a schedule:
        - First ask what tasks they would like the day to be scheduled around, and if any have to be at a specific time. Do not ask about specific times beyond the initial inquiry. If you have generated the tasks for the user, just use the tasks you generated.
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
        - If the user wants to add a schedule to their calendar, you need to ask what day.
        For generating tasks:
        - Remember the main task that the user wants to complete
        - Your job is to break the main task into smaller tasks. An example of this is if the user says they want to clean their room, you could tell them to put laundry away, pick up trash, make their bed, etc.
        - Present the various tasks in a list format.
        - Then, ask if the user would like to remove any tasks that you have generated, or if they would like to add any of their own. Adjust the list accordingly.
        - Once the user is okay with the generated list, ask if they would like you to generate a schedule out of those tasks.
        - If they would like you to generate a schedule out of those tasks, follow the steps for generating a schedule using the tasks you listed out.
        - So you have to propose a schedule with times listed out for each generated task, ask the user if there's any changes they want to make, then ask if they'd like the schedule added to their calendar, and if so what date
        - Make sure that you ask if the generated schedule with the allocated times is okay with the user before adding it their calendar. You also have to ask what day they want to schedule the tasks for
        - Once they have said that they want a schedule generated, you are solely focused on that and no longer focused on task generation.

        Make sure to follow the instructions carefully while processing the request. 
        """}]


class BannerAndButtons:
    def __init__(self, master):
        self.master = master

        #default setting
        self.is_dark_mode = False

        #Variables
        self.dark_mode = {
            'main_bg': '#171717',
            'lighter_bg': "#494949",
            'text_fg': '#e1e1e1',
            'file': 'LogoBannerDark.png',
            'btn_theme_text': 'Light Mode',
            'btn_bg': '#cd4c4c',
            'btn_click': '#0097b2',
            'btn_fg': '#171717'
        }

        self.light_mode = {
            'main_bg': '#e1e1e1',
            'lighter_bg': '#ebebeb',
            'text_fg': '#171717',
            'file': 'LogoBannerLight.png',
            'btn_theme_text': 'Dark Mode',
            'btn_bg': '#0097b2',
            'btn_click': '#cd4c4c',
            'btn_fg': '#e1e1e1'
        }

        # banner
        self.banner = tk.PhotoImage(file='LogoBannerLight.png')
        self.banner_label = tk.Label(master, bg="#e1e1e1", image=self.banner, height=65, width=650)
        self.banner_label.grid(row=0, column=0, sticky='nsew')

        # will hold three buttons at top
        self.button_frame = Frame(master, bg='#e1e1e1')
        self.button_frame.grid(row=1, column=0, sticky='nsew', pady=(10, 0))  # total height = 165

        # first button
        self.dark_light_mode = Button(self.button_frame, text='Dark Mode', font=("Arial", 16), fg='#e1e1e1', bg='#0097b2', activebackground='#cd4c4c', activeforeground='#e1e1e1', command=self.toggle_both_themes)
        self.dark_light_mode.grid(row=0, column=0, sticky='nsew', padx=(10, 5))

        # second button
        self.login_button = Button(self.button_frame, text='Enter API Key', font=("Arial", 16), fg='#e1e1e1', bg='#0097b2', activebackground='#cd4c4c', activeforeground='#e1e1e1', command=self.open_api_window)
        self.login_button.grid(row=0, column=1, sticky='nsew', padx=(5, 5))

        # logged in/not logged in
        self.logged_in = False

        # third button
        self.open_cal_window_button = Button(self.button_frame, text="Go to Google Calendar", font=("Arial", 16), fg='#e1e1e1', bg='#0097b2', activebackground='#cd4c4c', activeforeground='#e1e1e1', command=self.open_cal_window)
        self.open_cal_window_button.grid(row=0, column=2, sticky='nsew', padx=(5, 10))

        # set weights of elements in button_frame
        self.button_frame.columnconfigure(0, weight=33)
        self.button_frame.columnconfigure(1, weight=33)
        self.button_frame.columnconfigure(2, weight=33)

        self.button_frame.rowconfigure(0, weight=1)

        # instantiate api_key_window widgets
        self.api_entry = None
        self.validity_label = None
        self.api_window = None

        # calls apply_theme to find the correct theme colors
        self.apply_theme(self.light_mode)

        # allow editing of Messaging
        self.instance_of_messages = None

    def set_instance_of_messaging(self, messaging):
        self.instance_of_messages = messaging

    # Calls both functions in both classes from clicking the one button
    def toggle_both_themes(self):
        self.instance_of_messages.toggle_theme_messages()
        self.toggle_theme_banner()

    # changes the colors
    def apply_theme(self, theme):
        self.master.config(bg=theme['main_bg'])
        self.banner_label.config(bg=theme['main_bg'])
        self.banner.config(file=theme['file'])
        self.button_frame.config(bg=theme['main_bg'])
        self.dark_light_mode.config(text=theme['btn_theme_text'], fg=theme['btn_fg'], bg=theme['btn_bg'], activebackground=theme['btn_click'], activeforeground=theme['btn_fg'])
        self.login_button.config(fg=theme['btn_fg'], bg=theme['btn_bg'], activebackground=theme['btn_click'], activeforeground=theme['btn_fg'])
        self.open_cal_window_button.config(fg=theme['btn_fg'], bg=theme['btn_bg'], activebackground=theme['btn_click'], activeforeground=theme['btn_fg'])

    # keeps track of which theme you're on
    def toggle_theme_banner(self):
        #this is how you toggle between themes and switch
        if self.is_dark_mode:
            self.apply_theme(self.light_mode)
        else:
            self.apply_theme(self.dark_mode)

        self.is_dark_mode = not self.is_dark_mode


    def open_api_window(self):
        global api_key, creds, service
        if not self.logged_in:
            # Configure the size and details of cal_window.
            self.api_window = Toplevel(self.master)
            self.api_window.geometry('200x100')

            # Create an input box for the user to enter their key, make it hidden.
            self.api_entry = Entry(self.api_window, show="", fg='grey')
            self.api_entry.grid(row=1, column=1)
            self.api_entry.insert(0, "Enter API Key Here")

            self.api_entry.bind("<FocusIn>", self.on_focus_in)
            self.api_entry.bind("<FocusOut>", self.on_focus_out)

            # text changes if api key is not valid
            self.validity_label = Label(self.api_window, text='')
            self.validity_label.grid(row=2, column=1)

            # bind the enter key to the submit button
            self.api_entry.bind("<Return>", self.submit)

            self.api_window.rowconfigure(0, weight=33)
            self.api_window.rowconfigure(1, weight=33)
            self.api_window.rowconfigure(2, weight=33)

            self.api_window.columnconfigure(0, weight=10)
            self.api_window.columnconfigure(1, weight=80)
            self.api_window.columnconfigure(2, weight=10)
        else:
            os.remove('token.json')
            self.logged_in = False
            self.login_button.config(text='Enter API Key')
            api_key = 'x'
            creds = None
            service = None

    def on_focus_in(self, event=None):
        # Remove default text when entry is focused
        if self.api_entry.get() == "Enter API Key Here":
            self.api_entry.delete(0, tk.END)
            self.api_entry.config(show="*", fg='grey')

    def on_focus_out(self, event):
        if not self.api_entry.get():
            self.api_entry.insert(0, "Enter API Key Here")
            self.api_entry.config(show="", fg='grey')

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
            self.api_window.destroy()
            self.instance_of_messages.chat_history.config(state=NORMAL)
            self.instance_of_messages.chat_history.delete("1.0", END)
            self.instance_of_messages.chat_history.config(state=DISABLED)
            self.logged_in = True
            self.login_button.config(text='Log Out')
        else:
            self.validity_label.config(text="Invalid API Key Entered")
            self.api_entry.delete(0, END)

    def login(self):
        global creds, service
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', functions_object.SCOPES)
            service = build('calendar', 'v3', credentials=creds)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', functions_object.SCOPES)
                creds = flow.run_local_server(port=0)
                service = build('calendar', 'v3', credentials=creds)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

    def open_cal_window(self):
        webbrowser.open_new("https://calendar.google.com/calendar/u/0/r")

class Messaging:
    def __init__(self, master):
        self.master = master

        # set default
        self.is_dark_mode = False

        # Variables, same as above
        self.dark_mode = {
            'main_bg': '#171717',
            'lighter_bg': "#494949",
            'text_fg': '#e1e1e1',
            'file': 'LogoBannerDark.png',
            'btn_theme_text': 'Light Mode',
            'btn_bg': '#0097b2',
            'btn_click': '#cd4c4c',
            'mic_color': '#e1e1e1'
        }

        self.light_mode = {
            'main_bg': '#e1e1e1',
            'lighter_bg': '#ebebeb',
            'text_fg': '#171717',
            'file': 'LogoBannerLight.png',
            'btn_theme_text': 'Dark Mode',
            'btn_bg': '#0097b2',
            'btn_click': '#cd4c4c',
            'mic_color': '#171717'
        }

        # chat box
        self.chat_frame = Frame(master, bg='#e1e1e1')
        self.chat_frame.grid(row=2, column=0, pady=(10, 5), padx=(10, 0), sticky='nsew')

        self.chat_history = Text(self.chat_frame, wrap=WORD, state='disabled', bg='#ebebeb', fg='#171717')
        self.chat_history.grid(row=0, column=0, sticky='nsew')

        # vertical scrollbar for chat_history
        self.scrollbar = Scrollbar(self.chat_frame, bg='purple', command=self.chat_history.yview)
        self.scrollbar.grid(row=0, column=1, sticky='nsew')
        self.chat_history.config(yscrollcommand=self.scrollbar.set)

        # chat_frame weights
        self.chat_frame.columnconfigure(0, weight=97)
        self.chat_frame.columnconfigure(1, weight=3)
        self.chat_frame.rowconfigure(0, weight=1)

        # user input frame
        self.input_frame = Frame(master, bg='#e1e1e1')
        self.input_frame.grid(row=3, sticky='nsew')

        # Create an input box for the user to send a message to the prompt.
        self.user_input = Entry(self.input_frame, fg='grey', bg='#e1e1e1', font=("TkFixedFont", 12))
        self.user_input.grid(row=0, column=0, sticky='nsew', padx=(10))
        self.user_input.insert(0, "Message AICalendar...")

        # bind the entry key to the send button
        self.user_input.bind("<Return>", self.send)
        # set the colors of text inside user_input
        self.user_input.bind("<FocusIn>", self.on_focus_in)
        self.user_input.bind("<FocusOut>", self.on_focus_out)

        # voice input button
        self.voice_button = Button(self.input_frame, text='🎤', bg='#e1e1e1', fg='#171717', font=(3), command=self.voice_input)
        self.voice_button.grid(row=0, column=1, sticky='nsew', padx=(5, 10))
        self.recognizer = sr.Recognizer()
        self.voice_audio = None
        self.voice_text = None
        self.voice_button_listening = False

        # gap for padding at the bottom
        self.input_padding = Frame(master, bg = '#e1e1e1')
        self.input_padding.grid(row=4, sticky='nsew')

        # gap for padding at the bottom
        self.input_padding = Frame(master, bg = '#e1e1e1')
        self.input_padding.grid(row=4, sticky='nsew')

        # set the weights for the size of the elements
        self.input_frame.columnconfigure(0, weight=97)
        self.input_frame.columnconfigure(1, weight=3)
        self.input_frame.rowconfigure(0, weight=1)

        self.apply_theme(self.light_mode)

        # allow editing of other class
        self.banner_and_buttons_instance = None

    def set_banner_and_buttons_instance(self, b_and_b):
        self.banner_and_buttons_instance = b_and_b

    def apply_theme(self, theme):
        self.master.config(bg=theme['main_bg'])
        self.input_frame.config(bg=theme['main_bg'])
        self.user_input.config(bg=theme['lighter_bg'], fg=theme['text_fg'])
        self.voice_button.config(bg=theme['lighter_bg'], fg=theme['mic_color'])
        #self.scrollbar.config(troughcolor=theme['lighter_bg'])
        self.chat_frame.config(bg=theme['main_bg'])
        self.chat_history.config(bg=theme['lighter_bg'], fg=theme['text_fg'])
        self.input_padding.config(bg=theme['main_bg'])


    def toggle_theme_messages(self):
        #this is how you toggle between themes and switch
        if self.is_dark_mode:
            self.apply_theme(self.light_mode)
        else:
            self.apply_theme(self.dark_mode)

        self.is_dark_mode = not self.is_dark_mode

    def on_focus_in(self, event=None):
        # Remove default text when entry is focused
        if self.user_input.get() == "Message AICalendar...":
            self.user_input.delete(0, tk.END)

            # white or black depending on dark/light mode
            if self.is_dark_mode:
                self.user_input.config(fg='white')
                self.user_input.config(insertbackground='white')
            else:
                self.user_input.config(fg='black')
                self.user_input.config(insertbackground='black')

    def on_focus_out(self, event):
        if not self.user_input.get():
            self.user_input.insert(0, "Message AICalendar...")
            self.user_input.config(fg='grey')

    def send(self, event=None):
        global api_key, messages, functions
        if api_key != 'x':
            self.chat_history.config(state=NORMAL)
            self.chat_history.insert(END, "\n" + "You: ", "bold")
            self.chat_history.insert(END, self.user_input.get() + "\n")
            self.chat_history.tag_configure("bold", font=("TkFixedFont", 9, "bold"))

            messages.append({"role": "user", "content": self.user_input.get()})

            self.user_input.delete(0, END)

            # calling chat_completion_request to call ChatGPT completion endpoint
            chat_response = functions_object.chat_completion_request(messages, functions=functions, function_call=None,
                                                    model=functions_object.GPT_MODEL,
                                                    api_key=api_key)

            # fetch response of ChatGPT and call the function
            assistant_message = chat_response.json()["choices"][0]["message"]

            if assistant_message['content']:
                self.chat_history.insert(END, "Assistant: ", "bold")
                self.chat_history.insert(END, assistant_message['content'] + "\n" + "\n")
                messages.append({"role": "assistant", "content": assistant_message['content']})
                self.chat_history.tag_configure("bold", font=("TkFixedFont", 9, "bold"))
            else:
                # assistant message is a dictionary
                # extracts the name of the function to be called
                fn_name = assistant_message["function_call"]["name"]
                # extracts the arguments required for the function call
                arguments = assistant_message["function_call"]["arguments"]
                # retrieves the actual function that corresponds to the name
                function = getattr(functions_object, fn_name)
                # uses the retrieved function  with arguments as the parameter
                result = function(arguments, service)
                self.chat_history.insert(END, "\n" + "Assistant: ", "bold")
                self.chat_history.insert(END, result + "\n")
                self.chat_history.tag_configure("bold", font=("TkFixedFont", 9, "bold"))

            self.chat_history.see(END)
            self.chat_history.config(state=DISABLED)
        else:
            self.chat_history.config(state=NORMAL)
            self.user_input.delete(0, END)
            self.chat_history.delete("1.0", END)
            self.chat_history.insert(END, "Please Enter API Key")
            self.chat_history.see(END)
            self.chat_history.config(state=DISABLED)

    def voice_input(self):
        self.user_input.delete(0, END)
        with sr.Microphone() as source:
            self.voice_audio = self.recognizer.listen(source)
        try:
            self.voice_text = self.recognizer.recognize_google(self.voice_audio)
            self.user_input.insert(END, self.voice_text)
        except:
            self.user_input.delete(0, END)
            self.user_input.insert(END, "Voice Input not recognized, try again")


functions_object = ChatFunctions()
api_key = "x"
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', functions_object.SCOPES)
    service = build('calendar', 'v3', credentials=creds)
else:
    service = None
    creds = None


def main():
    main_wind = Tk()

    instance_of_messages = Messaging(main_wind)
    instance_banner = BannerAndButtons(main_wind)

    instance_of_messages.set_banner_and_buttons_instance(instance_banner)
    instance_banner.set_instance_of_messaging(instance_of_messages)

    main_wind.rowconfigure(0, weight=15)
    main_wind.rowconfigure(1, weight=17)
    main_wind.rowconfigure(2, weight=53)
    main_wind.rowconfigure(3, weight=10)
    main_wind.rowconfigure(4, weight=5)
    main_wind.columnconfigure(0, weight=1)

    main_wind.focus_force()
    main_wind.title("Virtual Assistant")
    main_wind.geometry('680x650')
    main_wind.mainloop()


if __name__ == "__main__":
    main()


