import os
import yagmail
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv("config.env")

# Load config
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
SLACK_TOKEN = os.getenv("SLACK_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL")
REPORT_PATH = "test-report.html"

def send_email():
    try:
        yag = yagmail.SMTP(GMAIL_USER, GMAIL_APP_PASSWORD)
        subject = "📊 Selenium Test Report"
        body = "Hi,\n\nAttached is the latest Selenium test report.\n\nRegards,\nAutomation Bot"
        yag.send(to=GMAIL_USER, subject=subject, contents=body, attachments=REPORT_PATH)
        print("✅ Email sent.")
    except Exception as e:
        print(f"❌ Email failed: {e}")

def send_slack_message():
    client = WebClient(token=SLACK_TOKEN)
    try:
        # Upload file
        result = client.files_upload(
            channels=SLACK_CHANNEL,
            file=REPORT_PATH,
            title="📊 Selenium Test Report"
        )
        print("✅ Report uploaded to Slack.")
    except SlackApiError as e:
        print(f"❌ Slack error: {e.response['error']}")

if __name__ == "__main__":
    if os.path.exists(REPORT_PATH):
        send_email()
        send_slack_message()
    else:
        print("❌ Report not found.")
