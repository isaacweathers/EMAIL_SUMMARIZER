import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
from collections import defaultdict
import re

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

def extract_date_from_email(email_body):
    """Extract date from email body using common patterns."""
    # Common date patterns
    date_patterns = [
        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}',  # March 15, 2024
        r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}',    # 15 March 2024
        r'\d{4}-\d{2}-\d{2}',                                                       # 2024-03-15
        r'\d{2}/\d{2}/\d{4}'                                                        # 03/15/2024
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, email_body)
        if match:
            try:
                date_str = match.group(0)
                # Convert various formats to datetime
                for fmt in ["%b %d, %Y", "%d %b %Y", "%Y-%m-%d", "%m/%d/%Y"]:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue
            except Exception:
                continue
    
    # Default to current date if no date found
    return datetime.now()

def analyze_email(email_body, subject):
    """Analyze a single email using OpenAI's API for summary, category, and sentiment."""
    try:
        # Truncate email body if it's too long (OpenAI has token limits)
        max_length = 4000  # Adjust based on your needs
        truncated_body = email_body[:max_length] + "..." if len(email_body) > max_length else email_body
        
        # Create a prompt for the analysis
        prompt = f"""Subject: {subject}

Email content:
{truncated_body}

Please analyze this email and provide:
1. A concise 2-3 sentence summary
2. Category (choose one): Marketing, Professional, Personal, Newsletter, Job/Recruitment, Financial, Technical, Other
3. Primary sentiment (choose one): Positive, Negative, Neutral, Urgent
4. Priority (choose one): High, Medium, Low
5. Key points (up to 3 bullet points)

Format your response exactly like this:
SUMMARY: [your summary]
CATEGORY: [category]
SENTIMENT: [sentiment]
PRIORITY: [priority]
KEY POINTS:
- [point 1]
- [point 2]
- [point 3]"""
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes emails concisely and accurately."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.3,
        )
        
        # Extract the analysis from the response
        analysis = response.choices[0].message.content.strip()
        
        # Parse the response into structured data
        parts = analysis.split('\n')
        result = {
            'summary': '',
            'category': '',
            'sentiment': '',
            'priority': '',
            'key_points': [],
            'date': extract_date_from_email(email_body)
        }
        
        current_section = None
        for part in parts:
            if part.startswith('SUMMARY:'):
                result['summary'] = part.replace('SUMMARY:', '').strip()
            elif part.startswith('CATEGORY:'):
                result['category'] = part.replace('CATEGORY:', '').strip()
            elif part.startswith('SENTIMENT:'):
                result['sentiment'] = part.replace('SENTIMENT:', '').strip()
            elif part.startswith('PRIORITY:'):
                result['priority'] = part.replace('PRIORITY:', '').strip()
            elif part.startswith('KEY POINTS:'):
                current_section = 'key_points'
            elif current_section == 'key_points' and part.strip().startswith('-'):
                result['key_points'].append(part.strip()[2:].strip())
        
        return result
    except Exception as e:
        print(f"Error analyzing email: {str(e)}")
        return {
            'summary': f"Error: Could not analyze this email. {str(e)}",
            'category': 'Error',
            'sentiment': 'Unknown',
            'priority': 'Unknown',
            'key_points': [],
            'date': datetime.now()
        }

def analyze_time_trends(analyzed_emails):
    """Analyze trends over time."""
    # Sort emails by date
    sorted_emails = sorted(analyzed_emails, key=lambda x: x['analysis']['date'])
    
    # Initialize trend data structures
    trends = {
        'categories_by_month': defaultdict(lambda: defaultdict(int)),
        'sentiments_by_month': defaultdict(lambda: defaultdict(int)),
        'priorities_by_month': defaultdict(lambda: defaultdict(int)),
        'volume_by_month': defaultdict(int)
    }
    
    # Analyze trends
    for email in sorted_emails:
        date = email['analysis']['date']
        month_key = date.strftime('%Y-%m')
        
        # Count emails by month
        trends['volume_by_month'][month_key] += 1
        
        # Count categories, sentiments, and priorities by month
        trends['categories_by_month'][month_key][email['analysis']['category']] += 1
        trends['sentiments_by_month'][month_key][email['analysis']['sentiment']] += 1
        trends['priorities_by_month'][month_key][email['analysis']['priority']] += 1
    
    return trends

def save_analysis_report(analyzed_emails, output_file='email_analysis.txt'):
    """Save the analysis results to a formatted report."""
    with open(output_file, 'w') as f:
        f.write("EMAIL ANALYSIS REPORT\n")
        f.write("=" * 80 + "\n\n")
        
        # Calculate basic statistics
        categories = defaultdict(int)
        sentiments = defaultdict(int)
        priorities = defaultdict(int)
        
        for email in analyzed_emails:
            categories[email['analysis']['category']] += 1
            sentiments[email['analysis']['sentiment']] += 1
            priorities[email['analysis']['priority']] += 1
        
        # Calculate time-based trends
        trends = analyze_time_trends(analyzed_emails)
        
        # Write statistics
        f.write("SUMMARY STATISTICS\n")
        f.write("-" * 80 + "\n")
        
        f.write("\nCategories Distribution:\n")
        for cat, count in categories.items():
            f.write(f"- {cat}: {count} emails ({count/len(analyzed_emails)*100:.1f}%)\n")
        
        f.write("\nSentiment Distribution:\n")
        for sent, count in sentiments.items():
            f.write(f"- {sent}: {count} emails ({count/len(analyzed_emails)*100:.1f}%)\n")
        
        f.write("\nPriority Distribution:\n")
        for prio, count in priorities.items():
            f.write(f"- {prio}: {count} emails ({count/len(analyzed_emails)*100:.1f}%)\n")
        
        # Write time-based trends
        f.write("\nTIME-BASED ANALYSIS\n")
        f.write("-" * 80 + "\n")
        
        f.write("\nEmail Volume by Month:\n")
        for month in sorted(trends['volume_by_month'].keys()):
            count = trends['volume_by_month'][month]
            f.write(f"- {month}: {count} emails\n")
        
        f.write("\nCategory Trends by Month:\n")
        for month in sorted(trends['categories_by_month'].keys()):
            f.write(f"\n{month}:\n")
            for category, count in trends['categories_by_month'][month].items():
                f.write(f"  - {category}: {count} emails\n")
        
        f.write("\nSentiment Trends by Month:\n")
        for month in sorted(trends['sentiments_by_month'].keys()):
            f.write(f"\n{month}:\n")
            for sentiment, count in trends['sentiments_by_month'][month].items():
                f.write(f"  - {sentiment}: {count} emails\n")
        
        # Write detailed analysis
        f.write("\n\nDETAILED EMAIL ANALYSIS\n")
        f.write("=" * 80 + "\n\n")
        
        # Sort emails by date
        sorted_emails = sorted(analyzed_emails, key=lambda x: x['analysis']['date'])
        
        for i, email in enumerate(sorted_emails, 1):
            f.write(f"Email {i}: {email['subject']}\n")
            f.write("-" * 80 + "\n")
            f.write(f"Date: {email['analysis']['date'].strftime('%Y-%m-%d')}\n")
            f.write(f"Category: {email['analysis']['category']}\n")
            f.write(f"Sentiment: {email['analysis']['sentiment']}\n")
            f.write(f"Priority: {email['analysis']['priority']}\n")
            f.write(f"Summary: {email['analysis']['summary']}\n")
            f.write("\nKey Points:\n")
            for point in email['analysis']['key_points']:
                f.write(f"- {point}\n")
            f.write("\n" + "=" * 80 + "\n\n")
    
    print(f"\nDetailed analysis saved to {output_file}")

def analyze_emails(emails, max_emails=10):
    """Analyze multiple emails."""
    analyzed_emails = []
    
    # Limit the number of emails to process to avoid rate limits
    emails_to_process = emails[:max_emails]
    
    print(f"Analyzing {len(emails_to_process)} emails...")
    
    for i, email in enumerate(emails_to_process, 1):
        print(f"Processing email {i}/{len(emails_to_process)}: {email['subject'][:50]}...")
        analysis = analyze_email(email['body'], email['subject'])
        analyzed_emails.append({
            "subject": email['subject'],
            "analysis": analysis
        })
    
    return analyzed_emails

def main():
    """Main function to read emails and generate analysis."""
    try:
        # Read emails from emails.json
        print("Reading emails from emails.json...")
        with open('emails.json', 'r') as file:
            emails = json.load(file)
        
        print(f"Found {len(emails)} emails.")
        
        # Analyze emails
        analyzed_emails = analyze_emails(emails)
        
        # Save detailed analysis report
        save_analysis_report(analyzed_emails)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 