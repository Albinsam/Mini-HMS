import json
import smtplib
from email.message import EmailMessage

def send_notification(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        action = body.get('action') 
        recipient = body.get('email')
        
        if not recipient or not action:
            return {"statusCode": 400, "body": json.dumps({"error": "Missing email/action"})}

        msg = EmailMessage()
        msg['To'] = recipient
        msg['From'] = "albinsamthomas13@gmail.com"

        # Content based on the "Actions" required by your PDF
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

        # SENDING THE EMAIL
        # IMPORTANT: Use a Google App Password, NOT your regular password
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login('albinsamthomas13@gmail.com', 'dchh jrij nnpv ggmj')
            smtp.send_message(msg)

        print(f"Email Sent: {action} to {recipient}")
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Email sent successfully!"})
        }

    except Exception as e:
        print(f"Error: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}