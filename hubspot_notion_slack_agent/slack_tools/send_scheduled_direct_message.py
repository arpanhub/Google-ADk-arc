"""
Send scheduled direct message tool
"""
import os
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
from ._helpers import get_user_id_from_email

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
slack_client = WebClient(token=SLACK_BOT_TOKEN)


def send_scheduled_direct_message(
    user_email: str,
    message: str,
    scheduled_time: str
) -> str:
    """Send a scheduled direct message to a user."""
    try:
        user_id = get_user_id_from_email(user_email)
        if not user_id:
            return "error: user not found"
        
        try:
            if 'T' in scheduled_time:
                scheduled_dt = datetime.fromisoformat(scheduled_time)
            else:
                scheduled_dt = datetime.strptime(scheduled_time, "%Y-%m-%d %H:%M:%S")
            post_at = int(scheduled_dt.timestamp())
        except ValueError:
            return "error: invalid time format"
        
        current_time = int(datetime.now().timestamp())
        
        # Auto-adjust if time is in the past
        if post_at <= current_time:
            print(f"⚠️ Scheduled time is in the past, adjusting to 2 minutes from now")
            post_at = current_time + 120  # 2 minutes
        
        response = slack_client.chat_scheduleMessage(
            channel=user_id,
            text=message,
            post_at=post_at
        )
        
        scheduled_message_id = response.get("scheduled_message_id", "")
        if scheduled_message_id:
            scheduled_time_str = datetime.fromtimestamp(post_at).strftime('%Y-%m-%d %H:%M:%S')
            print(f"✅ Message scheduled for {user_email} at {scheduled_time_str}")
            return scheduled_message_id
        else:
            return "error: no scheduled_message_id returned"
        
    except SlackApiError as e:
        error_msg = e.response.get("error", "unknown")
        return f"error: {error_msg}"
    except Exception as e:
        return f"error: {str(e)}"
