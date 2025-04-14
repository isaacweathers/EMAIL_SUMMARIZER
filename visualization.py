import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import json

def load_analyzed_emails(file_path='emails.json'):
    """Load and parse the analyzed emails from the JSON file."""
    with open(file_path, 'r') as f:
        emails_data = json.load(f)
    
    # Convert the email data into a format suitable for visualization
    emails = []
    for email in emails_data:
        # Extract date from the email data
        date_str = email.get('date', datetime.now().strftime('%Y-%m-%d'))
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            date = datetime.now()
            
        email_data = {
            'date': date,
            'category': email.get('category', 'Uncategorized'),
            'sentiment': email.get('sentiment', 'Neutral'),
            'priority': email.get('priority', 'Normal'),
            'subject': email.get('subject', 'No Subject'),
            'summary': email.get('summary', 'No summary available'),
            'body': email.get('body', 'No content available')
        }
        emails.append(email_data)
    
    return emails

def create_category_distribution_chart(emails, output_file='category_distribution.png'):
    """Create a pie chart showing the distribution of email categories."""
    categories = {}
    for email in emails:
        category = email['category']
        categories[category] = categories.get(category, 0) + 1
    
    plt.figure(figsize=(10, 6))
    plt.pie(categories.values(), labels=categories.keys(), autopct='%1.1f%%')
    plt.title('Email Categories Distribution')
    plt.savefig(output_file)
    plt.close()

def create_sentiment_trend_chart(emails, output_file='sentiment_trend.png'):
    """Create a line chart showing sentiment trends over time."""
    df = pd.DataFrame(emails)
    df['month'] = df['date'].dt.to_period('M')
    sentiment_counts = df.groupby(['month', 'sentiment']).size().unstack(fill_value=0)
    
    plt.figure(figsize=(12, 6))
    for sentiment in sentiment_counts.columns:
        plt.plot(sentiment_counts.index.astype(str), sentiment_counts[sentiment], 
                marker='o', label=sentiment)
    
    plt.title('Sentiment Trends Over Time')
    plt.xlabel('Month')
    plt.ylabel('Number of Emails')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

def create_priority_distribution_chart(emails, output_file='priority_distribution.png'):
    """Create a bar chart showing the distribution of email priorities."""
    priorities = {}
    for email in emails:
        priority = email['priority']
        priorities[priority] = priorities.get(priority, 0) + 1
    
    plt.figure(figsize=(8, 6))
    plt.bar(priorities.keys(), priorities.values())
    plt.title('Email Priority Distribution')
    plt.xlabel('Priority Level')
    plt.ylabel('Number of Emails')
    plt.savefig(output_file)
    plt.close()

def generate_all_visualizations(emails):
    """Generate all visualization charts."""
    create_category_distribution_chart(emails)
    create_sentiment_trend_chart(emails)
    create_priority_distribution_chart(emails)
    print("Visualizations have been generated successfully!")

if __name__ == "__main__":
    emails = load_analyzed_emails()
    generate_all_visualizations(emails) 