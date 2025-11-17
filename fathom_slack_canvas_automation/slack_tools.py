import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from typing import Dict, Any
from datetime import datetime, timedelta
import json

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
slack_client = WebClient(token=SLACK_BOT_TOKEN) 


def get_current_time() -> str:
    """
    Gets the current date and time in ISO format.
    Useful for calculating due dates and reminder times.
    
    Returns:
        str: Current time in ISO format (YYYY-MM-DDTHH:MM:SS)
    
    Example:
        >>> current_time = get_current_time()
        >>> print(current_time)
        "2025-11-14T16:45:30"
    """
    now = datetime.now()
    iso_time = now.strftime("%Y-%m-%dT%H:%M:%S")
    print(f"⏰ Current time: {iso_time}")
    return iso_time


def calculate_future_time(base_time: str, add_minutes: int) -> str:
    """
    Calculates a future time by adding minutes to a base time.
    
    Args:
        base_time: Base time in ISO format (YYYY-MM-DDTHH:MM:SS)
        add_minutes: Number of minutes to add
    
    Returns:
        str: Future time in ISO format
    
    Example:
        >>> future = calculate_future_time("2025-11-14T16:45:30", 2)
        >>> print(future)
        "2025-11-14T16:47:30"
    """
    try:
        if 'T' in base_time:
            base_dt = datetime.fromisoformat(base_time)
        else:
            base_dt = datetime.strptime(base_time, "%Y-%m-%d %H:%M:%S")
        
        future_dt = base_dt + timedelta(minutes=add_minutes)
        future_time = future_dt.strftime("%Y-%m-%dT%H:%M:%S")
        
        print(f"📅 Base time: {base_time}")
        print(f"➕ Adding {add_minutes} minutes")
        print(f"🎯 Result: {future_time}")
        
        return future_time
    except Exception as e:
        print(f"❌ Error calculating future time: {str(e)}")
        return ""


def create_meeting_notes_canvas(
    channel_id: str,
    meeting_title: str,
    things_discussed: str,
    action_items: str,
    attendees: str = "", 
    meeting_date: str = "",
    additional_notes: str = ""
) -> str:
    """
    Creates a Slack Canvas with formatted meeting notes.
    
    Args:
        channel_id: Slack channel ID where canvas will be posted
        meeting_title: Title of the meeting
        things_discussed: JSON array string of discussion points, e.g. '["Point 1", "Point 2"]'
        action_items: JSON array string of action items, e.g. '[{"task_title": "Task 1", "owner_name": "John"}]'
        attendees: Comma-separated attendee names (e.g., "John, Sarah, Mike")
        meeting_date: Meeting date string (e.g., "2024-03-20")
        additional_notes: Additional notes text
    
    Returns:
        str: Canvas ID if successful, empty string if failed
    """
    print("📝 Creating meeting notes canvas...")
    
    try:
        # Parse JSON strings
        try:
            things_discussed_list = json.loads(things_discussed) if things_discussed else []
        except:
            things_discussed_list = []
        
        try:
            action_items_list = json.loads(action_items) if action_items else []
        except:
            action_items_list = []
        
        # Parse attendees
        attendee_list = []
        if attendees:
            attendee_list = [name.strip() for name in attendees.split(",") if name.strip()]
        
        # Build canvas content
        content_parts = [f"# {meeting_title}\n\n"]

        if meeting_date:
            content_parts.append(f"📅 *Date:* {meeting_date}\n\n")
        
        if attendee_list:
            content_parts.append("## 👥 Attendees\n")
            for attendee in attendee_list:
                content_parts.append(f"- {attendee}\n")
            content_parts.append("\n")
        
        if things_discussed_list:
            content_parts.append("## 💬 Things Discussed\n")
            for idx, item in enumerate(things_discussed_list, 1):
                content_parts.append(f"{idx}. {item}\n")
            content_parts.append("\n")
        
        if action_items_list:
            content_parts.append("## 📝 Action Items\n")
            for item in action_items_list:
                if isinstance(item, str):
                    content_parts.append(f"- [ ] {item}\n")
                elif isinstance(item, dict):
                    task = item.get("task_title") or item.get("description") or "Untitled Task"
                    owner = item.get("owner_name", "Unassigned")
                    due = item.get("due_date", "")
                    
                    line = f"- [ ] {task} → *{owner}*"
                    if due:
                        line += f" (Due: {due})"
                    content_parts.append(line + "\n")
            content_parts.append("\n")
        
        if additional_notes:
            content_parts.append("## 📌 Additional Notes\n")
            content_parts.append(f"{additional_notes}\n\n")
        
        markdown_content = "".join(content_parts)
        
        print("="*50)
        print(markdown_content)
        print("="*50)
        
        document_content = {
            "type": "markdown",
            "markdown": markdown_content
        }
        
        payload = {
            "title": meeting_title,
            "document_content": document_content
        }
        
        if channel_id:
            payload["channel_id"] = channel_id
        
        response = slack_client.canvases_create(**payload)
        
        if response.get("ok"):
            canvas_id = response.get("canvas_id", "")
            print(f"✅ Canvas created: {canvas_id}")
            return canvas_id
        else:
            error_msg = response.get("error", "Unknown error")
            print(f"❌ Failed: {error_msg}")
            return f"error: {error_msg}"
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return f"error: {str(e)}"


def create_task_reminder(
    user_email: str,
    task_title: str,
    task_description: str,
    due_date: str,
    reminder_advance_hours: int = 24
) -> str:
    """
    Create task reminders for multiple users before due date.
    
    Args:
        user_email: Comma-separated email addresses (e.g., "john@company.com, sarah@company.com")
        task_title: Title of the task
        task_description: Description of the task
        due_date: Due date in ISO format (YYYY-MM-DDTHH:MM:SS)
        reminder_advance_hours: Hours before due date to send reminder
    
    Returns:
        str: Success message with scheduled IDs or error message
    """
    print(f"⏰ Creating task reminder: {task_title}")
    
    email_list = [email.strip() for email in user_email.split(",") if email.strip()]
    
    if not email_list:
        return "error: no valid email addresses provided"
    
    try:
        if 'T' in due_date:
            due_date_obj = datetime.fromisoformat(due_date)
        else:
            due_date_obj = datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        print(f"❌ Invalid date format: {due_date}")
        return "error: invalid date format"
    
    reminder_time = due_date_obj - timedelta(hours=reminder_advance_hours)
    
    # ✅ NEW: If reminder time is in the past, set it to 2 minutes from now
    current_time = datetime.now()
    if reminder_time <= current_time:
        print(f"⚠️ Reminder time is in the past, setting to 2 minutes from now")
        reminder_time = current_time + timedelta(minutes=2)
        print(f"🎯 New reminder time: {reminder_time}")

    message = f"""📋 *Task Reminder*
*{task_title}*
{task_description}
*Due Date:* {due_date_obj.strftime('%Y-%m-%d %H:%M')}
*Reminder:* {reminder_advance_hours}h before (adjusted if needed)"""
    
    results = []
    for email in email_list:
        scheduled_id = send_scheduled_direct_message(email, message, reminder_time.isoformat())
        if scheduled_id.startswith("error"):
            results.append(f"{email}: {scheduled_id}")
        else:
            results.append(f"{email}: scheduled ({scheduled_id})")
    
    return "; ".join(results)


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
        
        # ✅ NEW: Auto-adjust if time is in the past
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
            print(f"✅ Scheduled message to {user_email} at {scheduled_time_str}")
            return scheduled_message_id
        else:
            return "error: no message id"
        
    except SlackApiError as e:
        error_msg = e.response.get("error", "unknown")
        return f"error: {error_msg}"
    except Exception as e:
        return f"error: {str(e)}"


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
            print(f"✅ Found user: {user.get('id')}")
            return user
        else:
            print(f"❌ User not found: {email}")
            return {}
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {}