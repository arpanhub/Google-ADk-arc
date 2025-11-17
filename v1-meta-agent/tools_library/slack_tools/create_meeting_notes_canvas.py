"""
Create meeting notes canvas tool
"""
import os
import json
from slack_sdk import WebClient
from dotenv import load_dotenv

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
slack_client = WebClient(token=SLACK_BOT_TOKEN)


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
                task = item.get("task_title", item.get("description", ""))
                owner = item.get("owner_name", "Unassigned")
                due = item.get("due_date", "")
                
                line = f"- [ ] **{task}**"
                if owner and owner != "Unassigned":
                    line += f" - *Owner:* {owner}"
                if due:
                    line += f" - *Due:* {due}"
                line += "\n"
                content_parts.append(line)
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
