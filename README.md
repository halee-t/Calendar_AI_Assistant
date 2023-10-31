# Team5_AI_Assistant
This project has been created for a Software Engineering (CSI 3370) class at Oakland University by Halee Tisler, Nick Steiner, Shekia Tillerson, Mike Sadowski, and Will Toland.

## Overview
Our AI Assistant shall provide organization for the user's schedule by adding/deleting events from your calendar or generating a suggested schedule based on user input. The system will receive typed input from the user as instructions for the AI Assistant, where it will then make calls to the OpenAI API. Our AI Assistant should provide language support, personalized filters and customization, and an option for voice commands. Our system should be displayed with a pleasing UI with an optional dark mode.

## Common Problems
- If you are getting error messages saying that your token has **expired** or been **revoked**, delete the `token.json` file and rerun the code. It will force you to re-login.
- If you are getting an error message with `Key Error: 'choices'`, try generating a new API Key or connecting to a VPN.

## Credits
Our project is based on the [Appointment Booking Chatbot](https://www.pragnakalp.com/how-to-use-openai-function-calling-to-create-appointment-booking-chatbot/) created by Pragnakalp. 