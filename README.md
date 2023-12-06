# Team5_AI_Assistant
This project has been created for a Software Engineering (CSI 3370) class at Oakland University by Halee Tisler, Nick Steiner, Shekia Tillerson, Mike Sadowski, and Will Toland.

## Overview
Our AI Assistant shall provide organization for our user's busy schedule. They will be able to add, delete, and edit events while also checking their availability. The generation feature allows you to use AI to generate either a suggested schedule based on a list of tasks you wish to complete, or a list of minitasks to break down one provided main task. Once these are generated and customized to your liking, you can add it straight to your calendar! The system will receive typed input from the user as instructions for the AI Assistant, where it will then make calls to the OpenAI API. Our AI Assistant should provide language support, voice-to-text, visuals themes, and customization. The Calendar AI Assistant allows for a perfect schedule made by you, for you.

## Common Problems
- If you are getting error messages saying that your token has **expired** or been **revoked**, delete the `token.json` file and rerun the code. It will force you to re-login.
- If you are getting an error message with `Key Error: 'choices'`, try generating a new API Key or connecting to a VPN.
- Make sure you have all necessary imports

## Credits
Our project is based on the [Appointment Booking Chatbot](https://www.pragnakalp.com/how-to-use-openai-function-calling-to-create-appointment-booking-chatbot/) created by Pragnakalp. 
