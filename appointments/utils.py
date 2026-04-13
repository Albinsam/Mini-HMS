import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from django.utils import timezone
import pytz

# This scope allows us to read and write to the calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']

def create_calendar_event(summary, start_time, end_time, attendee_email):
    """
    Handles the OAuth2 flow and creates an event in the user's Google Calendar.
    """
    creds = None
    
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # This looks for the credentials.json file you downloaded from Google Console
            if not os.path.exists('credentials.json'):
                print("Error: credentials.json not found in project root.")
                return None
                
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            # This opens your default web browser for the login
            creds = flow.run_local_server(port=0, open_browser=True)
            
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Build the Calendar Service
        service = build('calendar', 'v3', credentials=creds)

        # 1. Convert times to Kolkata timezone explicitly
        # This ensures the string sent to Google matches the 'timeZone' label
        
        kolkata_tz = pytz.timezone('Asia/Kolkata')
        localized_start = start_time.astimezone(kolkata_tz)
        localized_end = end_time.astimezone(kolkata_tz)

        # SAFETY CHECK: If end time is the same as start time, add 30 minutes
        if localized_start == localized_end:
            from datetime import timedelta
            localized_end = localized_start + timedelta(minutes=30)
            print("DEBUG: End time was empty, added 30 mins automatically.")
        # Build the attendees list dynamically
        attendee_list = []
        if attendee_email and "@" in attendee_email:
            attendee_list.append({'email': attendee_email})

        event = {
            'summary': summary,
            'description': 'Appointment booked via Mini Hospital Management System.',
            'start': {
                'dateTime': localized_start.isoformat(), # Now has the +05:30 offset
                'timeZone': 'Asia/Kolkata', 
            },
            'end': {
                'dateTime': localized_end.isoformat(),
                'timeZone': 'Asia/Kolkata',
            },
            'attendees': attendee_list,
        }
        
        # Insert the event
        event_result = service.events().insert(calendarId='primary', body=event).execute()
        
        print(f"Event created successfully!")
        return event_result.get('htmlLink')

    except Exception as e:
        print(f"An error occurred: {e}")
        return None