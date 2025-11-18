import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from typing import Dict, Any, Optional,List
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
    
    Example:
        >>> action_items = [
        ...     {
        ...         "task_title": "Update documentation",
        ...         "owner_name": "John Doe",
        ...         "owner_email": "john@company.com",
        ...         "due_date": "2024-03-20"
        ...     }
        ... ]
        >>> result = create_meeting_notes_canvas(
        ...     channel_id="C123456",
        ...     meeting_title="Sprint Planning",
        ...     things_discussed=["Project timeline", "Resource allocation"],
        ...     action_items=action_items,
        ...     attendees=["John", "Sarah", "Mike"]
        ... )
    """
    # ✅ FIX: Handle None default properly
    if attendees is None:
        attendees = []
    things_discussed = things_discussed or []
    agenda = agenda or []
    meeting_date = meeting_date or ""
    additional_notes = additional_notes or ""
    decisions = decisions or []
    action_items = action_items or []

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
    due_date: str,  # ✅ FIX: Changed from Union[datetime, str] to just str
    reminder_advance_hours: int = 24
) -> Dict[str, Optional[str]]:
    """
    Create task reminders for multiple users before due date.
    Requires OAuth scopes: chat:write, users:read.email

    Args:
        user_email: List of user email addresses
        task_title: Title of the task
        task_description: Description of the task
        due_date: Due date in ISO format (YYYY-MM-DDTHH:MM:SS) or (YYYY-MM-DD HH:MM:SS)
        reminder_advance_hours: Hours before due date to send reminder (default 24)
    
    Returns:
        Dict mapping email to scheduled message ID (None if failed for that user)
    
    Example:
        >>> result = create_task_reminder(
        ...     user_email=["john@company.com", "sarah@company.com"],
        ...     task_title="Complete Q4 Report",
        ...     task_description="Finalize and submit the quarterly report",
        ...     due_date="2024-12-31T17:00:00",
        ...     reminder_advance_hours=24
        ... )
    """
    # ✅ Parse string to datetime
    try:
        # Try ISO format first: "2024-12-31T17:00:00"
        if 'T' in due_date:
            due_date_obj = datetime.fromisoformat(due_date)
        else:
            # Try space-separated format: "2024-12-31 17:00:00"
            due_date_obj = datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        print(f"✗ Invalid date format: {due_date}")
        print(f"  Expected: 'YYYY-MM-DDTHH:MM:SS' or 'YYYY-MM-DD HH:MM:SS'")
        return {email: None for email in user_email}
    
    # Calculate reminder time
    reminder_time = due_date_obj - timedelta(hours=reminder_advance_hours)
    
    # Check if reminder time is in the future
    if reminder_time <= datetime.now():
        print(f"✗ Error: Reminder time ({reminder_time}) is in the past!")
        print(f"   Due date: {due_date_obj}")
        print(f"   Advance hours: {reminder_advance_hours}")
        print(f"   Suggestion: Increase due_date or decrease reminder_advance_hours")
        return {email: None for email in user_email}

    message = f"""📋 *Task Reminder*
*{task_title}*
{task_description}
*Due Date:* {due_date_obj.strftime('%Y-%m-%d %H:%M')}
*Reminder sent:* {reminder_advance_hours} hours before due date"""
    
    results = {}
    for email in user_email:
        scheduled_id = send_scheduled_direct_message(email, message, reminder_time)
        results[email] = scheduled_id
    
    return results

def send_scheduled_direct_message(
    user_email: str,
    message: str,
    scheduled_time: str  # ✅ FIX: Changed from Union to just str
) -> Optional[str]:
    """
    Send a scheduled direct message to a user by email.
    Requires OAuth scopes: chat:write, users:read.email
    
    Args:
        user_email: User's email address
        message: Message text to send
        scheduled_time: Time to send in ISO format (YYYY-MM-DDTHH:MM:SS) or Unix timestamp
    
    Returns:
        str: Scheduled message ID if successful, None otherwise
    
    Example:
        >>> send_scheduled_direct_message(
        ...     user_email="john@company.com",
        ...     message="Meeting in 1 hour!",
        ...     scheduled_time="2024-12-20T14:00:00"
        ... )
    """
    try:
        # Get user ID from email
        user_id = get_user_id_from_email(user_email)
        if not user_id:
            print(f"✗ Could not find user: {user_email}")
            return None
        
        # ✅ Parse scheduled_time - handle both string and int
        if isinstance(scheduled_time, str):
            try:
                # Try ISO format
                if 'T' in scheduled_time:
                    scheduled_dt = datetime.fromisoformat(scheduled_time)
                else:
                    # Try space-separated
                    scheduled_dt = datetime.strptime(scheduled_time, "%Y-%m-%d %H:%M:%S")
                post_at = int(scheduled_dt.timestamp())
            except ValueError:
                # Assume it's already a Unix timestamp string
                post_at = int(scheduled_time)
        elif isinstance(scheduled_time, datetime):
            post_at = int(scheduled_time.timestamp())
        else:
            post_at = int(scheduled_time)
        
        # Verify time is in the future
        current_time = int(datetime.now().timestamp())
        if post_at <= current_time:
            print(f"✗ Scheduled time must be in the future")
            print(f"   Current time: {datetime.fromtimestamp(current_time)}")
            print(f"   Requested time: {datetime.fromtimestamp(post_at)}")
            return None
        
        # Schedule the message
        response = slack_client.chat_scheduleMessage(
            channel=user_id,
            text=message,
            post_at=post_at
        )
        
        scheduled_message_id = response.get("scheduled_message_id")
        scheduled_time_str = datetime.fromtimestamp(post_at).strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"✓ Scheduled message to {user_email} for {scheduled_time_str}")
        print(f"  Message ID: {scheduled_message_id}")
        
        return scheduled_message_id
        
    except SlackApiError as e:
        error_msg = e.response.get("error", "unknown")
        print(f"✗ Slack API error: {error_msg}")
        
        if error_msg == "time_in_past":
            print(f"  The scheduled time is in the past. Please provide a future time.")
        elif error_msg == "not_in_channel":
            print(f"  Bot needs to be added to the channel or have access to DM the user")
        
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
