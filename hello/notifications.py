import requests
import json
import os
import dotenv

dotenv.load_dotenv()

url = "https://slack.com/api/chat.postMessage"

slack_api_key = str(os.environ.get("SLACK_API_KEY"))


def send_notification(endpoint, project, data):
    payload = json.dumps({
    "channel": "#nara-error-logs",
    "blocks": [
        {
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": "Error :warning:"
        }
        },
        {
        "type": "divider"
        },
        {
        "type": "section",
        "text": {
            "type": "plain_text",
            "text": "Something has happened"
        }
        },
        {
        "type": "section",
        "fields": [
            {
            "type": "mrkdwn",
            "text": f"*Endpoint:*\n{endpoint}"
            },
            {
            "type": "mrkdwn",
            "text": f"*Project:*\n{project}"
            }
        ]
        },
        {
        "type": "divider"
        },
        {
        "type": "section",
        "fields": [{"type": "mrkdwn", "text": f"*{data[0]}:*\n{data[1]}"} for item in data]
        }
    ],
    "username": "Nara watchbot"
    })
    headers = {
        'Authorization': f"Bearer {slack_api_key}",
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)


