import json
import time
from openai import OpenAI, RateLimitError
from flask import Flask, render_template

# Load the API key from a file
with open('secrets/openai.txt', 'r') as file:
    api_key = file.read().strip()

# Initialize OpenAI client with the API key from the file
client = OpenAI(
    api_key=api_key,
)

def load_emails_from_file(filename='smaller-set.json'):
    with open(filename, 'r') as f:
        emails = json.load(f)
    return emails

def summarize_email(email_body):
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Summarize the following email:\n\n{email_body}",
            }
        ],
        model="chatgpt-4o-latest",
    )
    return response['choices'][0]['message']['content'].strip()

def summarize_email_with_retry(email_body, retries=3, delay=10):
    for attempt in range(retries):
        try:
            return summarize_email(email_body)
        except RateLimitError:
            print(f"Rate limit exceeded, retrying in {delay} seconds...")
            time.sleep(delay)
    print("Failed after several attempts due to rate limiting.")
    return "Summary not available due to rate limiting."

def summarize_emails(emails):
    summarized_emails = []
    for email in emails:
        summary = summarize_email_with_retry(email['body'])
        summarized_emails.append({
            "subject": email['subject'],
            "summary": summary
        })
        time.sleep(1)  # Add a delay of 1 second between requests
    return summarized_emails

app = Flask(__name__)

@app.route('/')
def index():
    emails = load_emails_from_file()
    summarized_emails = summarize_emails(emails)
    return render_template('index.html', emails=summarized_emails)

if __name__ == '__main__':
    app.run(debug=True)
