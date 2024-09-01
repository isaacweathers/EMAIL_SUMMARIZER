from __future__ import print_function
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os.path
import json

# Define the scope for Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('secrets/client_secret_117428019088-tatqct6jl7k40pqqgbtnai6cpb23t1n5.apps.googleusercontent.com.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def get_emails(service):
    try:
        results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
        messages = results.get('messages', [])
        emails = []
        for msg in messages:
            msg = service.users().messages().get(userId='me', id=msg['id']).execute()
            payload = msg['payload']
            headers = payload.get("headers")
            subject = None
            for header in headers:
                if header['name'] == 'Subject':
                    subject = header['value']
            if payload.get("body").get("data"):
                data = payload.get("body").get("data")
            else:
                data = payload.get("parts")[0]["body"]["data"]
            decoded_data = base64.urlsafe_b64decode(data.encode("UTF-8")).decode("UTF-8")
            emails.append({"subject": subject, "body": decoded_data})
        return emails
    except HttpError as error:
        print(f'An error occurred: {error}')

def main():
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)
    emails = get_emails(service)
    return emails

def save_emails_to_file(emails, filename='emails.json'):
    with open(filename, 'w') as f:
        json.dump(emails, f, indent=4)
        
if __name__ == '__main__':
    emails = main()
    print(emails)
    save_emails_to_file(emails)
    print("Emails saved to emails.json")
