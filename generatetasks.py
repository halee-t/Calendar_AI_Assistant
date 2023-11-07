import openai
import os

# API KEY Remind to delete before pushing!!!
openai.api_key = "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"


## Play around with this some more. Work towards modifying the instructions for chatGPT
def generateSchedule():
  # Create a list to store all the messages for context

  # TODO: Mess with this more, When I added the Instructions I started getting a timeout error
  messages = [
    {"role": "system", "content": f"""You are a helpful calendar assistant. Your job is to create a schedule for the user to follow based on inputted tasks from the user that they would like to get done during the day.
     You have to remember the time that the user would like to start and end their day and the start time of any events that the user specifies.
    
    Instructions:
    - If a user request is ambiguous, then you need to ask for clarification.
    - Remember the adjustments that the user is making to the suggested schedule in the active run.
    - If the user does not specify when they would like to start and end their day, please ask and adjust accordingly.
    - If the user would like to study, include 15 minute breaks between all consecutive study periods
    - If the user specifies a time they have an event at, that event MUST start at that time always.
    - If the user mentions breakfast, it must start between 7AM and 11AM unless otherwise specified.
    - If the user mentions lunch, it must start between 12PM and 3PM unless otherwise specified.
    - If the user mentions dinner, it must start between 5PM and 7PM unless otherwise specified.
    - After generating the schedule, ask if the user would like to make any adjustments
    
    Make sure to follow the instructions carefully while processing the request.  
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
  print("\nHello! Provide me with the tasks you would like to complete and I can generate a schedule for you.")
  generateSchedule()