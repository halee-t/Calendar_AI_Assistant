from tkinter import *
from tkinter import messagebox
import openai
import os
import sqlite3
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

conn = sqlite3.connect("chat_database.db")  #creates connection with database / if db doesnt exist it will create one
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_database'")
table_exists = cursor.fetchone()
global user_input_2
global response_text


if table_exists is None:
    conn.execute("create table chat_database(chats text)") # creates chat history table in db if it doesnt exist with a collumn for chats


openai.api_key = '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'
message_history = []  #this will store previous chats

#pre set the instructions for the AI
instruction = "Hi, I want you to work as a software engineer to help me generate a UML diagram. Based off of a project description you will return mermaid code that the user can create a UML diagram with."


def get_completion(prompt, model="gpt-3.5-turbo-16k"):
    update_history()
    message_history.append({"role": "user", "content": prompt})
    response = openai.ChatCompletion.create(
        model = model,
        messages = message_history,
        temperature = 0)
    reply = response["choices"][0]["message"]["content"]
    send_to_database(prompt, reply)
    clear_database()
    message_history.append({"role": "system", "content": reply})  # Append the user's message to message_history
    

    return response.choices[0].message["role"], response.choices[0].message["content"]

def send_to_database(prompt, reply):
    cursor.execute("insert into chat_database(chats) values(?)" , (prompt,))
    cursor.execute("insert into chat_database(chats) values(?)" , (reply,))
    conn.commit()

def clear_database():
    cursor.execute("SELECT COUNT(*) FROM chat_database")
    count = cursor.fetchone()[0]
    print(count)
    if count > 30:
        cursor.execute("DELETE FROM chat_database")
        conn.commit()
        messagebox.showinfo("Chat Cleared", "The chat history has been cleared.")
    message_history.append({"role": "system", "content": instruction})

def update_history():
    cursor.execute("SELECT * FROM chat_database")
    message_history = cursor.fetchall()

def GPTCall():
    global user_input_2
    user_input_2_text = user_input_2.get()
    role, response_content = get_completion(user_input_2_text)
    
    # Display "user:" or "bot:" based on the role and user input
    response_text.insert(END, "User: " + user_input_2_text + "\n\n")
    
    #output the ai response to the text field
    response_text.insert(END, "AI: " + response_content + "\n\n")
        
    # Clear the input text area
    user_input_2.delete(0, END)
    
def main():
    cursor.execute("DELETE FROM chat_database")
    conn.commit()
    message_history.append({"role": "system", "content": instruction})

    window = Tk()
    window.geometry("900x500")
    window.title("GPT-3 UML Diagram Generator")
    window.config(background="cyan")

    user_input_2 = Entry(window)
    user_input_2.place(x=100, y=430, width=700, height=100)

    label = Label(window, text="Demo Bot", font=("Arial", 24, "bold"))
    label.place(x=350, y=20)

    button = Button(window, text="Send", command=GPTCall)
    button.place(x=40, y=430)

    response_text = Text(window, wrap=WORD, font=("Arial", 12))
    response_text.place(x=50, y=80, width=800, height=300)

    scrollbar = Scrollbar(window, command=response_text.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    response_text.config(yscrollcommand=scrollbar.set)

    window.resizable(False, False)

    window.mainloop()

if __name__ == "__main__":
    main()