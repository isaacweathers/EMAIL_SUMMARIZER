import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

def summarize_email(email_body):
    messages = client.chat.completions.create(
        engine="text-davinci-003",
        prompt=f"Summarize the following email:\n\n{email_body}",
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return messages.choices[0].text.strip()

def summarize_emails(emails):
    summarized_emails = []
    for email in emails:
        summary = summarize_email(email['body'])
        summarized_emails.append(summary)
    return summarized_emails

# Read emails from emails.json
with open('emails.json', 'r') as file:
    emails = json.load(file)

summarized_emails = summarize_emails(emails)
for summary in summarized_emails:
    print(summary)