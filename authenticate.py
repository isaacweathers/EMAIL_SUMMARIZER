from __future__ import print_function
import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
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

if __name__ == '__main__':
    print("Starting Gmail authentication process...")
    authenticate_gmail()
    print("Authentication completed successfully!") 