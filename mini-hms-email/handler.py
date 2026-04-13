import os
import json
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# Load variables from the .env file
load_dotenv()

def send_notification(event, context):
    try:
        # 1. Parse the incoming data
        body = json.loads(event.get('body', '{}'))
        action = body.get('action') 
        recipient = body.get('email')
        
        if not recipient or not action:
            return {"statusCode": 400, "body": json.dumps({"error": "Missing email/action"})}

        # 2. Build the Email Message
        msg = EmailMessage()
        msg['To'] = recipient
        msg['From'] = "albinsamthomas13@gmail.com"

        if action == "SIGNUP_WELCOME":
            msg['Subject'] = "Welcome to Mini-HMS!"
            username = body.get('username', 'User')
            msg.set_content(f"Hello {username},\n\nWelcome to our Hospital Management System! Your account is active.")
        
        elif action == "BOOKING_CONFIRMATION":
            msg['Subject'] = "Appointment Confirmed"
            doctor = body.get('doctor', 'the Doctor')
            time = body.get('time', 'scheduled time')
            msg.set_content(f"Success! Your appointment with Dr. {doctor} is confirmed for {time}.")
        
        else:
            return {"statusCode": 400, "body": json.dumps({"error": "Unknown Action"})}

        # 3. SEND THE EMAIL using the environment variable
        # We use os.getenv to pull the password safely from .env
        gmail_user = "albinsamthomas13@gmail.com"
        gmail_password = os.getenv('EMAIL_PASSWORD')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(gmail_user, gmail_password)
            smtp.send_message(msg)

        print(f"Email Sent: {action} to {recipient}")
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Email sent successfully!"})
        }

    except Exception as e:
        print(f"Error: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}