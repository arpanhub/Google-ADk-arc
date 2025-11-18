"""
Create task reminder tool
"""
import os
from datetime import datetime, timedelta
from slack_sdk import WebClient
from dotenv import load_dotenv
from .send_scheduled_direct_message import send_scheduled_direct_message

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
slack_client = WebClient(token=SLACK_BOT_TOKEN)


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
    
    # If reminder time is in the past, set it to 2 minutes from now
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
