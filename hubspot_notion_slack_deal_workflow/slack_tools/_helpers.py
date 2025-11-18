"""
Internal helper functions for Slack tools
"""
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
slack_client = WebClient(token=SLACK_BOT_TOKEN)


def get_user_id_from_email(email: str) -> str:
    """Get Slack user ID from email address."""
    user = get_user_by_email(email)
    if user:
        return user.get("id", "")
    return ""


def get_user_by_email(email: str) -> Dict[str, Any]:
    """Look up a Slack user by email address."""
    try:
        response = slack_client.users_lookupByEmail(email=email)
        
        if response.get("ok"):
            user = response.get("user", {})
            print(f"✅ Found user: {user.get('real_name')} ({email})")
            return user
        else:
            print(f"❌ User not found: {email}")
            return {}
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {}
