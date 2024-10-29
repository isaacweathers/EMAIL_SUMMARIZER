from __future__ import print_function
from flask import Flask, render_template
import base64
import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Initialize Flask app
app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Define the scope for Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    """Authenticate the user and return Google API credentials."""
    creds = None

    # Load the client secret path from the environment variable
    client_secret_path = os.getenv("GOOGLE_CLIENT_SECRET_PATH")
    if not client_secret_path:
        raise ValueError("Client secret path not set. Check your environment variables.")

    # Check if token.json exists to reuse credentials
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If no valid credentials are found, initiate the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials to token.json for reuse
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

def get_emails(service):
    """Retrieve emails from the user's Gmail inbox."""
    try:
        # List the messages in the user's inbox
        results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
        messages = results.get('messages', [])
        emails = []

        # Fetch details for each message
        for msg in messages:
            msg = service.users().messages().get(userId='me', id=msg['id']).execute()
            payload = msg.get('payload', {})
            headers = payload.get('headers', [])

            # Extract subject from headers
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')

            # Decode the message body
            body_data = payload.get('body', {}).get('data')
            if not body_data and 'parts' in payload:
                body_data = payload['parts'][0].get('body', {}).get('data', '')

            decoded_body = base64.urlsafe_b64decode(body_data.encode('UTF-8')).decode('UTF-8')
            emails.append({"subject": subject, "body": decoded_body})

        return emails
    except HttpError as error:
        print(f'An error occurred: {error}')
        return []

@app.route('/')
def index():
    """Render the index page with a list of emails."""
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)
    emails = get_emails(service)
    return render_template('index.html', emails=emails)

if __name__ == '__main__':
    app.run(debug=True)
