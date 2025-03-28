from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import logging
from datetime import datetime

# Your Slack Bot Token
SLACK_BOT_TOKEN = "xoxb-7650621434417-8461255620961-ZhEkJsTUmnyLIGb8nWYjvQdc"
CHANNEL_ID = "#suspicious_ips"

# Initialize Slack Client
client = WebClient(token=SLACK_BOT_TOKEN)

def send_slack_message(msg):
    """Sends an alert message to Slack with a button to open the dashboard."""
    try:
        response = client.chat_postMessage(
            channel=CHANNEL_ID,
            attachments=[
                {
                    "color": "#ff0000", 
                    "blocks": [
                        {
                            "type": "header",
                            "text": {
                                "type": "plain_text",
                                "text": "🚨 Alert Notification! 🚨",
                                "emoji": True
                            }
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"📢 *Message:* ```{msg}```"
                            }
                        },
                        {
                            "type": "context",
                            "elements": [
                                {
                                    "type": "mrkdwn",
                                    "text": f"🕒 Timestamp: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`"
                                }
                            ]
                        },
                        {
                            "type": "divider"
                        },
                        {
                            "type": "actions",
                            "elements": [
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "✅ Acknowledge",
                                        "emoji": True
                                    },
                                    "style": "primary",
                                    "value": "acknowledged"
                                },
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "🔍 View Dashboard",
                                        "emoji": True
                                    },
                                    "style": "danger",
                                    "url": "http://127.0.0.1:5000/",  # Redirect to Web Dashboard
                                    "action_id": "view_dashboard"
                                }
                            ]
                        }
                    ]
                }
            ]
        )
        logging.info("Slack message sent successfully.")
    except SlackApiError as e:
        logging.error(f"Error sending Slack message: {e.response['error']}")

# Example Usage
if __name__ == "__main__":
    send_slack_message("Suspicious IP detected! 🚨 Check the dashboard for details.")
