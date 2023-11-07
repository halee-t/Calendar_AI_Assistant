import openai
import os

# API KEY Remind to delete before pushing!!!
openai.api_key = "x"


## Play around with this some more. Work towards modifying the instructions for chatGPT
def generateSchedule():
  # Create a list to store all the messages for context

  # TODO: Mess with this more, When I added the Instructions I started getting a timeout error
  messages = [
    {"role": "system", "content": f"""You are a helpful calendar assistant. Your job is to create a schedule for the user to follow based on inputted tasks from the user that they would like to get done during the day.
    
    Instructions:
    - If a user request is ambiguous, then also you need to ask for clarification.
    - Remember the adjustments that the user is making to the suggested schedule in the active run.
    - If the user does not say if they want their schedule to be mostly in the morning, midday, evening, or night, please ask.
    - If the user would like to study, include 15 minute breaks between consecutive study periods
    - If the user specifies a time they have an event at, DO NOT move the time of that event.
    """}
  ]

  # Keep repeating the following
  while True:
    # Prompt user for input
    message = input("User: ")

    # Exit program if user inputs "quit"
    if message.lower() == "quit":
      break

    # Add each new message to the list
    messages.append({"role": "user", "content": message})

    # Request gpt-3.5-turbo for chat completion
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=messages
    )

    # Print the response and add it to the messages list
    chat_message = response['choices'][0]['message']['content']
    print(f"AI Assistant: {chat_message}")
    messages.append({"role": "assistant", "content": chat_message})

if __name__ == "__main__":
  print("Start chatting with the bot (type 'quit' to stop)!")
  generateSchedule()