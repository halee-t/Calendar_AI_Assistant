from tkinter import *
from tkinter import filedialog
import webbrowser

main_wind= Tk()

main_wind.title("Virtual Assistant")
main_wind.geometry('440x540')
# Change the default bg from white to black
# window.configure(bg='#333333')

#Creating a label widget for the API key
myLabel = Label(main_wind, text="Enter your API key.")
myLabel.grid(row=0, column=0, padx=10)

#Create an input box for the user to enter their key, make it hidden.
api_entry = Entry(main_wind, width=30, show = "*")
api_entry.grid(row=0, column=2, pady=20)


#This is what will happen when the submit button is pressed.
#-----------I want it to go to the next input box after the API is put in, will fix this later.
def submit():
    api_key = "secret"
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

# This defines the send button, and what happens when you press it.
def send():
    if prompt_entry.get():
        myLabel4 = Label(main_wind, text="Okay, I will put this in your calendar!")
        myLabel4.grid(row=11, column=2)
    

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
open_next.grid(row=20, column=2, padx=15)
 

#---------- Not sure if I need this line: main_wind.mainloop()
mainloop()