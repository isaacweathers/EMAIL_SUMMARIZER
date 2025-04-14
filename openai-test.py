import os
import json
import openai
from dotenv import load_dotenv
import tiktoken

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI with API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def summarize_email(email_body):
    """Summarize the provided email body using the OpenAI API."""
    print(f"Summarizing Email Body:\n{email_body}\n")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o", 
            messages=[
                {
                    "role": "user",
                    "content": f"Summarize the following email:\n\n{email_body}",
                }
            ],
        )
        return response.choices[0].message.content.strip()  
    except openai.error.InvalidRequestError as e:
        print(f"Error: Request exceeds token limit: {e}")
        return None  # Or handle differently, e.g., split the email
    except Exception as e:
        print(f"Error in API call: {e}")
        return None

def summarize_emails(emails):
    """Process a list of emails and return their summaries."""
    summarized_emails = []
    
    for email in emails:
        # Safely extract the email body
        body = email.get('body', '').strip()  # Corrected line
        if not body:
            print("Warning: Email body is missing or empty.")
            continue
        
        num_tokens = num_tokens_from_string(body, "cl100k_base")
        print(f"Email body has {num_tokens} tokens")

        if num_tokens > 3500:  # Leave some room for the output tokens
            print("Warning: Email is too long to summarize effectively.")
            continue 

        try:
            summary = summarize_email(body)
            if summary:
                summarized_emails.append(summary)
        except Exception as e:
            print(f"Error summarizing email: {e}")
    
    return summarized_emails

# Load emails from emails.json and verify content
try:
    with open('emails.json', 'r', encoding='utf-8') as file:
        emails = json.load(file)

    # Debugging: Check the loaded email content
    print("Loaded Emails:", emails)

    # Optional: Print each email's subject and body for verification
    for email in emails:
        print(f"Subject: {email.get('subject')}, Body: {email.get('body')}")
except (json.JSONDecodeError, FileNotFoundError) as e:
    print(f"Error loading emails.json: {e}")
    emails = []  # Handle gracefully by setting an empty list

# Summarize the emails
if emails:
    summarized_emails = summarize_emails(emails)
    
    # Open the file for writing
    with open('summaries.txt', 'w') as f:  
        for summary in summarized_emails:
            print(summary)  # Print to console
            f.write(summary + '\n')  # Write to file
else:
    print("No emails to summarize.")