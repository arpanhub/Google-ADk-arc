"""
Fathom Integration Tools
handles webhook reception, validation, and data parsing
"""
import os 
import json
import requests
from typing import Dict, Any,Optional, Union, List
from dotenv import load_dotenv
load_dotenv()

def receive_fathom_webhook(payload: dict) -> dict:
    """
    Receives and validates Fathom webhook payload.
    This tool is the entry point for Fathom data ingestion.
    It validates the payload structure and extracts relevant fields and summary data.

    USE THIS WHEN: Fathom webhook automatically sends data to your endpoint.

    Args:
        payload(dict): Raw webhook payload from Fathom (flat structure, no "event" wrapper)
        
    Expected Payload Structure:
        {
            "title": "Quarterly Business Review",
            "meeting_title": "QBR 2025 Q1",
            "url": "https://fathom.video/xyz123",
            "share_url": "https://fathom.video/share/xyz123",
            "created_at": "2025-03-01T17:01:30Z",
            "scheduled_start_time": "2025-03-01T16:00:00Z",
            "scheduled_end_time": "2025-03-01T17:00:00Z",
            "recording_start_time": "2025-03-01T16:01:12Z",
            "recording_end_time": "2025-03-01T17:00:55Z",
            "transcript": [...],
            "default_summary": {
                "template_name": "general",
                "markdown_formatted": "## Summary\\n..."
            },
            "action_items": [
                {
                    "description": "Email revised proposal to client",
                    "assignee": {
                        "name": "Jane Doe",
                        "email": "jane.doe@acme.com",
                        "team": "Marketing"
                    }
                }
            ],
            "calendar_invitees": [
                {
                    "name": "Alice Johnson",
                    "email": "alice.johnson@acme.com",
                    "is_external": false
                }
            ],
            "recorded_by": {
                "name": "Alice Johnson",
                "email": "alice.johnson@acme.com"
            },
            "crm_matches": {...}
        }
    
    Returns:
        dict: Validated and normalized data
        {
            "status": "success",
            "call_id": str,
            "timestamp": str,
            "meeting_title": str,
            "url": str,
            "summary": str,
            "things_discussed": List[str],
            "key_actions": List[dict],
            "participants": List[str],
            "recorded_by": dict,
            "error": str (if status is error)
        }
    
    Example:
        >>> payload = {"title": "QBR", "meeting_title": "Q1 Review", ...}
        >>> result = recieve_fathom_webhook(payload)
        >>> print(result['status'])
        "success"
    """
    print("Inside the fathom_tools recieve_fathom_webhook function")
    
    try:
        # Validate payload is a dictionary
        if not isinstance(payload, dict):
            print("Error: Payload must be a dictionary")
            return {
                "status": "error",
                "error": "Payload must be a dictionary"
            }
        
        # Check for required fields (no "event" or "data" wrapper)
        required_fields = ["title", "created_at"]
        missing_fields = [field for field in required_fields if field not in payload]
        
        if missing_fields:
            print(f"Error: Missing required fields: {missing_fields}")
            return {
                "status": "error",
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }
        
        # Extract action items with full details
        action_items = []
        for item in payload.get("action_items", []):
            assignee = item.get("assignee", {})
            action_items.append({
                "description": item.get("description", ""),
                "owner_name": assignee.get("name"),
                "owner_email": assignee.get("email"),
                "team": assignee.get("team"),
                "timestamp": item.get("recording_timestamp"),
                "playback_url": item.get("recording_playback_url"),
                "completed": item.get("completed", False)
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
        
        # Parse summary to extract things_discussed
        summary_markdown = payload.get("default_summary", {}).get("markdown_formatted", "")
        things_discussed = []
        
        # Simple parsing: look for bullet points or lines after "Things Discussed" or "Discussion"
        if "## Things Discussed" in summary_markdown or "## Discussion" in summary_markdown:
            lines = summary_markdown.split('\n')
            in_discussion_section = False
            for line in lines:
                if "## Things Discussed" in line or "## Discussion" in line:
                    in_discussion_section = True
                    continue
                elif line.startswith("## "):
                    in_discussion_section = False
                elif in_discussion_section and line.strip().startswith("-"):
                    things_discussed.append(line.strip().lstrip("- "))
        
        # Build result
        result = {
            "status": "success",
            "call_id": payload.get("id"),  # Note: might not exist in this format
            "timestamp": payload.get("created_at"),
            "meeting_title": payload.get("meeting_title") or payload.get("title"),
            "url": payload.get("url"),
            "share_url": payload.get("share_url"),
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
        
        print(f"Successfully processed webhook for: {result['meeting_title']}")
        print(f"   - Participants: {len(participants)}")
        print(f"   - Action Items: {len(action_items)}")
        
        return result
        
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        return {
            "status": "error",
            "error": f"Failed to process webhook: {str(e)}"
        }

def process_user_fathom_payload(user_input: Union[str, dict]) -> dict:
    """
    Processes Fathom payload provided manually by a user (via chat, form, or copy-paste).
    Handles both JSON strings and dict objects, with intelligent parsing and validation.
    
    USE THIS WHEN: User manually provides Fathom meeting data (not from webhook)
    
    Args:
        user_input (Union[str, dict]): User-provided Fathom data in one of these formats:
            1. JSON string (copied from Fathom or webhook logs)
            2. Python dict (already parsed)
    
    Supported Input Formats:
        Format 1 - JSON String:
            '''
            {
                "title": "Sprint Planning",
                "meeting_title": "Q1 Sprint Planning",
                "created_at": "2025-03-01T17:01:30Z",
                "action_items": [...],
                "calendar_invitees": [...]
            }
            '''
        
        Format 2 - Dict:
            {
                "title": "Sprint Planning",
                "created_at": "2025-03-01T17:01:30Z",
                ...
            }
    
    Returns:
        dict: Standardized data (same format as receive_fathom_webhook)
        {
            "status": "success" | "error",
            "call_id": str,
            "timestamp": str,
            "meeting_title": str,
            "url": str,
            "share_url": str,
            "summary": str,
            "things_discussed": List[str],
            "key_actions": List[dict],
            "participants": List[dict],
            "recorded_by": dict,
            "recording_times": dict,
            "crm_matches": dict,
            "error": str (only if error)
        }
    
    Example Usage:
        # User pastes JSON string
        >>> json_str = '''
        ... {
        ...     "title": "Team Sync",
        ...     "created_at": "2025-03-01T17:01:30Z",
        ...     "action_items": [...]
        ... }
        ... '''
        >>> result = process_user_fathom_payload(json_str)
        >>> print(result['status'])
        "success"
        
        # User provides dict directly
        >>> payload_dict = {"title": "Meeting", "created_at": "2025-03-01T17:01:30Z"}
        >>> result = process_user_fathom_payload(payload_dict)
        >>> print(result['meeting_title'])
        "Meeting"
    """
    print("👤 Processing user-provided Fathom payload...")
    
    try:
        # Step 1: Handle different input types
        if isinstance(user_input, str):
            print("📄 Input type: JSON string")
            user_input_cleaned = user_input.strip()
            
            # Validate it looks like JSON
            if not (user_input_cleaned.startswith('{') or user_input_cleaned.startswith('[')):
                return {
                    "status": "error",
                    "error": "Input string must be valid JSON (should start with { or [)"
                }
            
            # Parse JSON string
            try:
                payload = json.loads(user_input_cleaned)
                print("✅ Successfully parsed JSON string")
            except json.JSONDecodeError as e:
                return {
                    "status": "error",
                    "error": f"Invalid JSON format: {str(e)}\n\nPlease ensure your JSON is properly formatted."
                }
        
        elif isinstance(user_input, dict):
            print("📦 Input type: Dictionary (already parsed)")
            payload = user_input
        
        else:
            return {
                "status": "error",
                "error": f"Unsupported input type: {type(user_input).__name__}. Must be string (JSON) or dict."
            }
        
        # Step 2: Validate it's actually a dict after parsing
        if not isinstance(payload, dict):
            return {
                "status": "error",
                "error": f"Parsed data is not a dictionary. Got: {type(payload).__name__}"
            }
        
        # Step 3: Use the webhook processing logic (same validation and extraction)
        print("🔄 Validating and normalizing payload...")
        result = receive_fathom_webhook(payload)
        
        if result.get("status") == "success":
            print(f"✅ User payload processed successfully: {result.get('meeting_title')}")
        else:
            print(f"❌ Validation failed: {result.get('error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return {
            "status": "error",
            "error": f"Failed to process user payload: {str(e)}"
        }

    """
    Processes user-provided Fathom webhook payload in string or dict format.
    Validates and extracts relevant fields for further processing.

    USE THIS WHEN: User manually provides Fathom webhook payload data.

    Args:
        user_input (str|dict): Raw webhook payload from Fathom as JSON string or dictionary.
        
    Returns:
        dict: Validated and normalized data (same structure as recieve_fathom_webhook)
    
    Example:
        >>> user_input = '{"title": "QBR", "meeting_title": "Q1 Review", ...}'
        >>> result = process_user_fathom_payload(user_input)
        >>> print(result['status'])
        "success"
    """
    print("Inside the fathom_tools process_user_fathom_payload function")
    
    try:
        # Parse input if it's a string
        if isinstance(user_input, str):
            try:
                payload = json.loads(user_input)
            except json.JSONDecodeError:
                print("Error: Invalid JSON string")
                return {
                    "status": "error",
                    "error": "Invalid JSON string"
                }
        elif isinstance(user_input, dict):
            payload = user_input
        else:
            print("Error: Input must be a JSON string or dictionary")
            return {
                "status": "error",
                "error": "Input must be a JSON string or dictionary"
            }
        
        # Reuse existing validation and extraction logic
        return recieve_fathom_webhook(payload)
        
    except Exception as e:
        print(f"Error processing user input: {str(e)}")
        return {
            "status": "error",
            "error": f"Failed to process user input: {str(e)}"
        }

def _extract_discussion_points(markdown: str) -> List[str]:
    """
    Internal helper: Extract discussion points from markdown summary.
    
    Args:
        markdown (str): Markdown formatted summary text
        
    Returns:
        List[str]: List of discussion points
    """
    things_discussed = []
    
    if not markdown:
        return things_discussed
    
    # Look for "Things Discussed" or "Discussion" section
    if "## Things Discussed" in markdown or "## Discussion" in markdown:
        lines = markdown.split('\n')
        in_discussion_section = False
        
        for line in lines:
            # Start of discussion section
            if "## Things Discussed" in line or "## Discussion" in line:
                in_discussion_section = True
                continue
            # End of discussion section (new heading)
            elif line.startswith("## "):
                in_discussion_section = False
            # Extract bullet points
            elif in_discussion_section and line.strip().startswith("-"):
                point = line.strip().lstrip("- ").strip()
                if point:
                    things_discussed.append(point)
    
    return things_discussed