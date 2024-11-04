from datetime import datetime, timedelta
import pickle
import os.path
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google_calendar():
    """Shows basic usage of the Google Calendar API."""
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('./private/token.pickle'):
        with open('./private/token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                './private/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('./private/token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('calendar', 'v3', credentials=creds)
    return service

def schedule_meeting(service, summary, location, description, start_time, end_time):
    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'America/Chicago',  # Adjust the timezone as needed
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'America/Chicago',  # Adjust the timezone as needed
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    return event.get("htmlLink")

if __name__ == '__main__':
    # Authenticate and create a service object
    service = authenticate_google_calendar()
    
    # Define event details
    summary = "Meeting with Team"
    location = "123 Main St, Anytown, USA"
    description = "Discussing project updates and next steps."
    start_time = datetime.now() + timedelta(days=1)  # Event starts 1 day from now
    end_time = start_time + timedelta(hours=1)       # Duration of 1 hour

    # Create the event
    schedule_meeting(service, summary, location, description, start_time, end_time)
