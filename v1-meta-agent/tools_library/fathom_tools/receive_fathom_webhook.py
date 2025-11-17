"""
Fathom webhook receiver tool
"""
from typing import Dict, Any
from ._helpers import extract_discussion_points


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
        things_discussed = extract_discussion_points(summary_markdown)
        
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
