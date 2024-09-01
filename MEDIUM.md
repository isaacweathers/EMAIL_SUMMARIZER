The basic synopsis of this is adventure is that I really want to be able to stay in the loop with all the happenings but do not want to just rely on another app to do so. So I created a generic email to use for all the subscrptions like ByteByteGo, Tl;DR, etc... that would send topics and info to my email so I could have them in one spot. Howver, seeing as I have not had time to run through that I realized that I needed some way to aggregate, sort, summarize and filter all of this information down into manageable chunks for me. 

This will be a multi-phase project that hoepfully will turn into something useful but at bare-minimum will at least let me get to play around with some code and AI along with my cloud accounts. I'll try and document as much as I can so that if someone is just bored as hell they too can follow along. 

Step 1: The prompt

```ChatGPT
I need a solution to read my Gmails, summarize them and produce an easy to ready summarized output that can be displayed on a web page. It should be grouped by content and sortable. 
```

The output:


To build a solution that reads your Gmail, summarizes the emails, and presents the output in a web-friendly format, grouped by content and sortable, you can follow these steps:

### 1. **Set Up Gmail API Access**
   - Go to the [Google Cloud Console](https://console.cloud.google.com/).
   - Create a new project and enable the Gmail API.
   - Create OAuth 2.0 credentials and download the `credentials.json` file.
   - Install the necessary Python libraries:

     ```bash
     pip install --upgrade google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
     pip install openai  # For summarization using OpenAI's GPT
     ```

### 2. **Authenticate and Read Emails**
   Create a Python script to authenticate and read emails:

   ```python
   from __future__ import print_function
   import os.path
   import base64
   from google.auth.transport.requests import Request
   from google.oauth2.credentials import Credentials
   from google_auth_oauthlib.flow import InstalledAppFlow
   from googleapiclient.discovery import build
   from googleapiclient.errors import HttpError

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
               flow = InstalledAppFlow.from_client_secrets_file(
                   'credentials.json', SCOPES)
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

   if __name__ == '__main__':
       emails = main()
       print(emails)
   ```

### 3. **Summarize Emails**
   You can use OpenAI's GPT-3.5 to summarize the content of the emails:

   ```python
   import openai

   openai.api_key = 'your-openai-api-key'

   def summarize_email(email_body):
       response = openai.Completion.create(
           engine="text-davinci-003",
           prompt=f"Summarize the following email:\n\n{email_body}",
           max_tokens=100,
           n=1,
           stop=None,
           temperature=0.7,
       )
       return response.choices[0].text.strip()

   def summarize_emails(emails):
       summarized_emails = []
       for email in emails:
           summary = summarize_email(email['body'])
           summarized_emails.append({
               "subject": email['subject'],
               "summary": summary
           })
       return summarized_emails

   if __name__ == '__main__':
       emails = main()
       summarized_emails = summarize_emails(emails)
       print(summarized_emails)
   ```

### 4. **Create a Web Interface**
   Use Flask or Django to display the summarized emails on a web page, grouped by content and sortable:

   ```python
   from flask import Flask, render_template

   app = Flask(__name__)

   @app.route('/')
   def index():
       emails = summarize_emails(main())
       return render_template('index.html', emails=emails)

   if __name__ == '__main__':
       app.run(debug=True)
   ```

   In `index.html`, you can use a table to display the emails, with options to sort them by subject, summary, etc.

   ```html
   <!DOCTYPE html>
   <html lang="en">
   <head>
       <meta charset="UTF-8">
       <meta name="viewport" content="width=device-width, initial-scale=1.0">
       <title>Email Summaries</title>
   </head>
   <body>
       <h1>Email Summaries</h1>
       <table>
           <thead>
               <tr>
                   <th>Subject</th>
                   <th>Summary</th>
               </tr>
           </thead>
           <tbody>
               {% for email in emails %}
               <tr>
                   <td>{{ email.subject }}</td>
                   <td>{{ email.summary }}</td>
               </tr>
               {% endfor %}
           </tbody>
       </table>
   </body>
   </html>
   ```

### 5. **Run the Application**
   Start the Flask application:

   ```bash
   python app.py
   ```

   Navigate to `http://127.0.0.1:5000/` in your browser to view the summarized emails.

### 6. **Deployment and Additional Features**
   - Deploy this application using AWS services like Elastic Beanstalk or an EC2 instance.
   - Consider using a database (like DynamoDB) to store the summarized emails for more advanced querying and filtering.

This solution provides a complete workflow from reading Gmail, summarizing emails, and displaying them on a web page with sorting and grouping functionalities.


Good enough for government work, let's start with that.

Step 2: The environment

I'll be swiching between my macbook ai and my windows studio but really any setup you have should be ok. 

I'll be using VS Code because although I was a JetBrains afficianado for years, I have slowly gone over to the dark side and embraced VS Code. That being said, I will also be using the dev containers setup with VS Code and Github and will have all this up in the Github repo. 

#TODO
Come back and describe more about this and ellaborate on how it goes. Be sure to go through the whole GoogleCloud account setup. 

## Setting up Google
- Need to enable the GMail API
- Setup the Desktop Client Key
- Make a secrets directory to keep the key
- ensure secrets directory is added to `.gitignore` to prevent it from being uploaded. 