import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from typing import Dict, Any, Optional,List,Union
from datetime import datetime,timedelta

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
slack_client = WebClient(token=SLACK_BOT_TOKEN) 


def create_meeting_notes_canvas(
    channel_id: str,
    meeting_title: str,
    things_discussed: List[str],
    action_items: List[Dict[str, Any]],
    attendees: Optional[List[str]] = None,  # ✅ FIX: Use Optional[List[str]]
    meeting_date: Optional[str] = None,
    additional_notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Creates a Slack Canvas with formatted meeting notes.
    
    Args:
        channel_id: Slack channel ID where canvas will be posted
        meeting_title: Title of the meeting
        things_discussed: List of discussion points
        action_items: List of action items with owner and due date
        attendees: Optional list of attendee names
        meeting_date: Optional meeting date string
        additional_notes: Optional additional notes
    
    Returns:
        dict: Canvas creation result with canvas_id and channel_id
    """
    # ✅ FIX: Handle None default
    if attendees is None:
        attendees = []
    if things_discussed is None:
        things_discussed = []
    if agenda is None:
        agenda = []
    if decisions is None:
        decisions = []
    if action_items is None:
        action_items = []
    if meeting_date is None:
        meeting_date = ""
    if additional_notes is None:
        additional_notes = ""

    content_parts = [f"*Meeting Title:* {meeting_title}"]

    if attendees:
        content_parts.append("\n## 👥 Attendees")
        for attendee in attendees:
            content_parts.append(f"- {attendee}")
        print("Attendees section added.")
    
    if agenda:
        content_parts.append("\n## 📋 Agenda")
        for idx, item in enumerate(agenda, 1):
            content_parts.append(f"{idx}. {item}")
        print("Agenda section added.")
    
    if decisions:
        content_parts.append("\n## ✓ Decisions")
        for decision in decisions:
            content_parts.append(f"- {decision}")
        print("Decisions section added.")
    
    if action_items:
        content_parts.append("\n## 📝 Action Items")
        for item in action_items:
            action = item.get("task_title", "Untitled Task")
            assignee = item.get("owner_name", "Unassigned")
            content_parts.append(f"- {action} → *{assignee}*")
        print("Action Items section added.")
    
    markdown_content = "".join(content_parts)
    print("Creating meeting notes canvas with content:")
    print(markdown_content)
    try:
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
        print("Slack API response:")
        print(response)
        
        if response.get("ok"):
            canvas_id = response.get("canvas_id")
            print(f"✓ Meeting notes canvas created: {canvas_id}")
            return canvas_id
        else:
            error_msg = response.get("error", "Unknown error")
            print(f"✗ Failed to create canvas: {error_msg}")
            return None
            
    except SlackApiError as e:
        print(f"✗ Slack API Error: {e.response.get('error', str(e))}")
        return None
    except Exception as e:
        print(f"✗ Error creating canvas: {str(e)}")
        return None
    
def create_task_reminder(
        user_email: List[str],
        task_title: str,
        task_description: str,
        due_date: Union[datetime,str],
        reminder_advance_hours:int = 24
) -> Dict[str,Optional[str]]:
    """ 
    Create task reminders for multiple users before due date.
    Requires OAuth scopes: chat:write, users:read.email

    Args:
        user_emails: List of user email addresses
        task_title: Title of the task
        task_description: Description of the task
        due_date: Due date as datetime object or ISO format string (YYYY-MM-DDTHH:MM:SS)
        reminder_advance_hours: Hours before due date to send reminder (default 24)
    
    Returns:
        Dict mapping email to scheduled message ID (None if failed for that user)
    Example:
        from datetime import datetime, timedelta

        due = datetime.now() + timedelta(days=3)

        results = create_task_reminder(
            user_emails=["john@company.com", "sarah@company.com"],
             task_title="Project Submission",
            task_description="Submit all project deliverables and documentation",
            due_date=due,
            reminder_advance_hours=24
        )

        for email, msg_id in results.items():
            if msg_id:
                print(f"✓ Reminder scheduled for {email}")
            else:
                print(f"✗ Failed for {email}")
    """
    if isinstance(due_date, str):
        try:
            due_date = datetime.fromisoformat(due_date)
        except:
            print("✗ Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
            return {}
    reminder_time = due_date - timedelta(hours=reminder_advance_hours)

    message = f"""📋 *Task Reminder*
*{task_title}*
{task_description}
*Due Date:* {due_date.strftime('%Y-%m-%d %H:%M')}
*Reminder sent:* {reminder_advance_hours} hours before due date"""
    
    results = {}
    for email in user_email:
        scheduled_id = send_scheduled_direct_message(email, message, reminder_time)
        results[email] = scheduled_id
    
    return results

def send_scheduled_direct_message(
    user_email: str,
    message_text: str,
    scheduled_time: Union[int, datetime, str]
) -> Optional[str]:
    """
    Send a scheduled direct message to a user by email.
    
    Requires OAuth scopes: chat:write, users:read.email
    
    Args:
        user_email: Email address of the recipient
        message_text: Message text to send
        scheduled_time: Unix timestamp, datetime object, or ISO format string (YYYY-MM-DDTHH:MM:SS)
    
    Returns:
        Scheduled message ID if successful, None otherwise
    
    Example:
        from datetime import datetime, timedelta
        
        # Schedule for 2 hours from now
        future = datetime.now() + timedelta(hours=2)
        msg_id = send_scheduled_direct_message(
            "john@company.com",
            "Don't forget to review the proposal!",
            future
        )
    """
    try:
        # Convert datetime to Unix timestamp if needed
        if isinstance(scheduled_time, datetime):
            post_at = int(scheduled_time.timestamp())
            print(f"Converted datetime to timestamp: {post_at}")
        elif isinstance(scheduled_time, str):
            # Try to parse ISO format datetime
            try:
                dt = datetime.fromisoformat(scheduled_time)
                post_at = int(dt.timestamp())
            except:
                print("✗ Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS) or Unix timestamp")
                return None
        else:
            post_at = int(scheduled_time)
        
        # Look up user by email to get user ID
        user_id = get_user_id_from_email(user_email)
        print(f"User ID for {user_email}: {user_id}")

        if not user_id:
            print(f"✗ Could not find user with email: {user_email}")
            return None
        
        # Schedule message to user
        response = slack_client.chat_scheduleMessage(
            channel=user_id,
            text=message_text,
            post_at=post_at
        )
        print("Slack API response:")
        print(response)

        
        if response.get("ok"):
            scheduled_msg_id = response.get("scheduled_message_id")
            print(f"✓ Direct message scheduled: {scheduled_msg_id}")
            return scheduled_msg_id
        else:
            error_msg = response.get("error", "Unknown error")
            print(f"✗ Failed to schedule message: {error_msg}")
            return None
            
    except SlackApiError as e:
        print(f"✗ Slack API Error: {e.response.get('error', str(e))}")
        return None
    except Exception as e:
        print(f"✗ Error scheduling message: {str(e)}")
        return None

def get_user_id_from_email(email:str) -> Optional[str]:
    """
    Get Slack user ID from email address.
    
    Requires OAuth scope: users:read.email
    
    Args:
        email: Email address of the user
    
    Returns:
        User ID (e.g., "U123ABC") if found, None otherwise
    
    Example:
        user_id = get_user_id_from_email("john@company.com")
        if user_id:
            print(user_id)  # U123ABC
    """
    user = get_user_by_email(email)
    print("in the get_user_id_from_email function")
    print(f"User lookup result: {user}")
    if user:
        return user.get("id")
    return None 

def get_user_by_email(email:str)-> Optional[Dict[str,Any]]:
    """
    Look up a Slack user by email address.
    
    Requires OAuth scope: users:read.email
    
    Args:
        email: Email address of the user
    
    Returns:
        User object dict if found, None otherwise
    
    Example:
        user = get_user_by_email("john@company.com")
        if user:
            print(user["id"])  # U123ABC
            print(user["real_name"])  # John Doe
    """
    print("Inside get_user_by_email function")
    try:
        response = slack_client.users_lookupByEmail(email=email)
        print("Slack API response:")
        print(response)
        
        if response.get("ok"):
            user = response.get("user", {})
            user_id = user.get("id")
            print(f"✓ User found: {user_id} ({email})")
            return user
        else:
            error_msg = response.get("error", "Unknown error")
            print(f"✗ User not found: {error_msg}")
            return None
            
    except SlackApiError as e:
        print(f"✗ Slack API Error: {e.response.get('error', str(e))}")
        return None
    except Exception as e:
        print(f"✗ Error looking up user: {str(e)}")
        return None

# def set_slack_reminder(user_id: str, text: str, time_str: str) -> dict:
    """
    Set a Slack reminder for a user.
    
    Args:
        user_id: Slack user ID (e.g., U12345)
        text: Reminder text
        time_str: When to remind (e.g., "in 2 days", "tomorrow at 9am")
        
    Returns:
        dict: Reminder creation result
    """
    token = os.getenv("SLACK_BOT_TOKEN")
    if not token:
        return {"status": "error", "message": "SLACK_BOT_TOKEN not configured"}
    
    client = WebClient(token=token)
    
    try:
        response = client.reminders_add(
            text=text,
            time=time_str,
            user=user_id
        )
        
        return {
            "status": "success",
            "reminder_id": response["reminder"]["id"],
            "message": f"Reminder set for user {user_id}"
        }
        
    except SlackApiError as e:
        return {
            "status": "error",
            "message": f"Slack API error: {e.response['error']}"
        }
