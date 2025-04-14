from __future__ import print_function
import base64
import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define the scope for Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    """Authenticate the user and return Google API credentials."""
    try:
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
                # Use a different approach for containerized environments
                auth_url, _ = flow.authorization_url(prompt='consent')
                print(f"\nPlease visit this URL to authorize the application: {auth_url}\n")
                auth_code = input("Enter the authorization code: ")
                flow.fetch_token(code=auth_code)
                creds = flow.credentials

            # Save the credentials to token.json for reuse
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
                print("Credentials saved to token.json")

        return creds
    except Exception as e:
        print(f"Authentication error: {str(e)}")
        raise

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

def display_emails(emails):
    """Display emails in the terminal."""
    if not emails:
        print("No emails found.")
        return

    print(f"\nFound {len(emails)} emails:\n")
    for i, email in enumerate(emails, 1):
        print(f"Email {i}:")
        print(f"Subject: {email['subject']}")
        print(f"Body: {email['body'][:200]}...")  # Show first 200 characters
        print("-" * 80)

def main():
    """Main function to authenticate and fetch emails."""
    print("Starting Gmail email fetcher...")
    
    # Authenticate with Gmail
    creds = authenticate_gmail()
    
    # Build the Gmail service
    service = build('gmail', 'v1', credentials=creds)
    
    # Get emails
    print("Fetching emails...")
    emails = get_emails(service)
    
    # Display emails
    display_emails(emails)
    
    # Save emails to file
    with open('emails.json', 'w') as f:
        json.dump(emails, f, indent=4)
    print("\nEmails saved to emails.json")

if __name__ == '__main__':
    main() 