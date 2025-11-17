"""
Fathom Integration Tools
handles webhook reception, validation, and data parsing
"""
import os 
import json
import requests
from typing import Dict, Any, List
from dotenv import load_dotenv
load_dotenv()

def receive_fathom_webhook(payload: dict) -> dict:
    """
    Receives and validates Fathom webhook payload.
    This tool is the entry point for Fathom data ingestion.
    It validates the payload structure and extracts relevant fields and summary data.

    USE THIS WHEN: Fathom webhook automatically sends data to your endpoint.

    Args:
        payload: Raw webhook payload from Fathom (flat structure, no "event" wrapper)
        
    Returns:
        dict: Validated and normalized data with status, call_id, meeting_title, things_discussed, key_actions, participants
    """
    print("🔔 Processing Fathom webhook payload...")
    
    try:
        if not isinstance(payload, dict):
            return {
                "status": "error",
                "error": "Payload must be a dictionary"
            }
        
        required_fields = ["title", "created_at"]
        missing_fields = [field for field in required_fields if field not in payload]
        
        if missing_fields:
            return {
                "status": "error",
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }
        
        # Extract action items
        action_items = []
        for item in payload.get("action_items", []):
            assignee = item.get("assignee", {})
            action_items.append({
                "description": item.get("description", ""),
                "task_title": item.get("description", ""),  # Add task_title alias
                "owner_name": assignee.get("name"),
                "owner_email": assignee.get("email"),
                "team": assignee.get("team"),
                "timestamp": item.get("recording_timestamp"),
                "playback_url": item.get("recording_playback_url"),
                "completed": item.get("completed", False),
                "due_date": ""  # Empty by default
            })
        
        # Extract participants
        participants = []
        for invitee in payload.get("calendar_invitees", []):
            participants.append({
                "name": invitee.get("name"),
                "email": invitee.get("email"),
                "is_external": invitee.get("is_external", False),
                "domain": invitee.get("email_domain")
            })
        
        # Parse summary
        summary_markdown = payload.get("default_summary", {}).get("markdown_formatted", "")
        things_discussed = _extract_discussion_points(summary_markdown)
        
        result = {
            "status": "success",
            "call_id": payload.get("id", ""),
            "timestamp": payload.get("created_at"),
            "meeting_title": payload.get("meeting_title") or payload.get("title"),
            "url": payload.get("url", ""),
            "share_url": payload.get("share_url", ""),
            "summary": summary_markdown,
            "things_discussed": things_discussed,
            "key_actions": action_items,
            "participants": participants,
            "recorded_by": payload.get("recorded_by", {}),
            "recording_times": {
                "scheduled_start": payload.get("scheduled_start_time"),
                "scheduled_end": payload.get("scheduled_end_time"),
                "actual_start": payload.get("recording_start_time"),
                "actual_end": payload.get("recording_end_time")
            },
            "crm_matches": payload.get("crm_matches", {})
        }
        
        print(f"✅ Processed: {result['meeting_title']}")
        print(f"   📊 Participants: {len(participants)}")
        print(f"   📝 Action Items: {len(action_items)}")
        print(f"   💬 Discussion Points: {len(things_discussed)}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {
            "status": "error",
            "error": f"Failed to process webhook: {str(e)}"
        }


def process_user_fathom_payload(user_input: str) -> dict:
    """
    Processes Fathom payload provided manually by a user as JSON string.
    
    USE THIS WHEN: User manually provides Fathom meeting data (not from webhook)
    
    Args:
        user_input: JSON string of Fathom payload
    
    Returns:
        dict: Standardized data (same format as receive_fathom_webhook)
    """
    print("👤 Processing user-provided Fathom payload...")
    
    try:
        if not isinstance(user_input, str):
            return {
                "status": "error",
                "error": f"Input must be a JSON string, got {type(user_input).__name__}"
            }
        
        user_input_cleaned = user_input.strip()
        
        if not (user_input_cleaned.startswith('{') or user_input_cleaned.startswith('[')):
            return {
                "status": "error",
                "error": "Input string must be valid JSON (should start with { or [)"
            }
        
        try:
            payload = json.loads(user_input_cleaned)
            print("✅ Successfully parsed JSON string")
        except json.JSONDecodeError as e:
            return {
                "status": "error",
                "error": f"Invalid JSON format: {str(e)}"
            }
        
        if not isinstance(payload, dict):
            return {
                "status": "error",
                "error": f"Parsed JSON must be an object, got {type(payload).__name__}"
            }
        
        print("🔄 Validating and normalizing payload...")
        result = receive_fathom_webhook(payload)
        
        if result.get("status") == "success":
            print(f"✅ User payload processed: {result.get('meeting_title')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {
            "status": "error",
            "error": f"Failed to process user payload: {str(e)}"
        }


def _extract_discussion_points(markdown: str) -> List[str]:
    """
    Internal helper: Extract discussion points from markdown summary.
    """
    things_discussed = []
    
    if not markdown:
        return things_discussed
    
    if "## Things Discussed" in markdown or "## Discussion" in markdown:
        lines = markdown.split('\n')
        in_discussion_section = False
        
        for line in lines:
            if "## Things Discussed" in line or "## Discussion" in line:
                in_discussion_section = True
                continue
            elif line.startswith("## "):
                in_discussion_section = False
            elif in_discussion_section and line.strip().startswith("-"):
                point = line.strip().lstrip("- ").strip()
                if point:
                    things_discussed.append(point)
    
    return things_discussed