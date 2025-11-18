"""
Fathom Integration Tools
handles webhook reception, validation, and data parsing
"""
import os 
import json
import requests
from typing import Dict, Any,Optional
from dotenv import load_dotenv
load_dotenv()

def recieve_fathom_webhook(payload: dict) -> dict:
    """
    Receives and validates Fathom webhook payload.
    This tool is the entry point for Fathom data ingestion.
    It validates the payload structure and extracts relevant fields and summary data.

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

def fetch_fathom_call_summary(call_id: str) -> dict:
    """
    Fetches call summary from Fathom API using call_id.
    Requires FATHOM_API_KEY to authenticate and retrieve summary data.
    
    Args:
        call_id(str): Unique identifier for the Fathom call.
        
    Returns:
        dict: Fathom call summary data
        {
            "status": "success",
            "call_id": str,
            "summary": str (markdown formatted),
            "things_discussed": List[str],
            "key_actions": List[dict],
            "raw_data": dict (full API response)
        }
    
    Example:
        >>> result = fetch_fathom_call_summary("100276517")
        >>> print(result['status'])
        "success"
    """
    api_key = os.getenv("FATHOM_API_KEY")
    print("using call_id:", call_id)
    print('using API key:', api_key)
    if not api_key:
        return {
            "status": "error",
            "error": "FATHOM_API_KEY not set in environment"
        }
    
    try:
        url = f"https://api.fathom.ai/external/v1/recordings/{call_id}/summary"
        headers = {"X-Api-Key": api_key}
#         curl --request GET \
#   --url https://api.fathom.ai/external/v1/recordings/101043441/summary \
#   --header 'X-Api-Key: VrOkmBIiyMetP0LBSZ82PA.zbXOjWwvphaommaYmK-S4k_6CvfkudVv3m5R5Yk4R98'

        response = requests.get(url, headers=headers)
        print("Fathom API response status code:", response.status_code)
        response.raise_for_status()
        data = response.json()
        
        # Extract summary from the response
        summary_data = data.get("summary", {})
        summary_markdown = summary_data.get("markdown_formatted", "")
        
        # Parse things_discussed from markdown
        things_discussed = []
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
        
        # Parse action items from markdown
        key_actions = []
        if "## Action Items" in summary_markdown or "## Actions" in summary_markdown:
            lines = summary_markdown.split('\n')
            in_action_section = False
            for line in lines:
                if "## Action Items" in line or "## Actions" in line:
                    in_action_section = True
                    continue
                elif line.startswith("## "):
                    in_action_section = False
                elif in_action_section and line.strip().startswith("-"):
                    action_text = line.strip().lstrip("- ")
                    # Try to extract owner if present (e.g., "Task - Owner Name")
                    if " - " in action_text:
                        parts = action_text.split(" - ", 1)
                        key_actions.append({
                            "description": parts[0].strip(),
                            "owner_name": parts[1].strip() if len(parts) > 1 else None,
                            "owner_email": None,
                            "due_date": None
                        })
                    else:
                        key_actions.append({
                            "description": action_text,
                            "owner_name": None,
                            "owner_email": None,
                            "due_date": None
                        })
        
        return {
            "status": "success",
            "call_id": call_id,
            "summary": summary_markdown,
            "things_discussed": things_discussed,
            "key_actions": key_actions,
            "raw_data": data
        }
        
    except requests.exceptions.HTTPError as e:
        return {
            "status": "error",
            "error": f"HTTP error fetching call summary: {e.response.status_code} - {e.response.text}"
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error": f"Network error fetching call summary: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to fetch call summary: {str(e)}"
        }


def parse_fathom_summary(data: dict) -> Dict[str, Any]:
    """
    Parses the summary data from Fathom (either from webhook or API call).
    Normalizes the data structure and extracts key information.
    
    Args:
        data(dict): Validated Fathom data from webhook or API
            Can be from:
            - recieve_fathom_webhook() output
            - fetch_fathom_call_summary() output
            
    Returns:
        dict: Structured summary data
        {
            'status': 'success'|'error',
            'call_id': str,
            'things_discussed': List[str],
            'key_actions': List[dict],
            'participants': List[dict],
            'error': str (if status is error)
        }

    Key Actions Structure:
        Each action item has:
        - task_title: str (or "description")
        - owner_name: str
        - owner_email: str (optional)
        - due_date: str (optional in ISO format)

    Example:
        >>> webhook_data = recieve_fathom_webhook(payload)
        >>> result = parse_fathom_summary(webhook_data)
        >>> print(len(result["key_actions"]))
        3
        
        >>> api_data = fetch_fathom_call_summary("100276517")
        >>> result = parse_fathom_summary(api_data)
        >>> print(result['status'])
        "success"
    """ 

    try:
        # Check if the input data has an error status
        if data.get('status') == 'error':
            return {
                'status': 'error',
                'error': f'Cannot parse failed data: {data.get("error")}'
            }
        
        # Extract data fields (handles both webhook and API response formats)
        things_discussed = data.get("things_discussed", [])
        key_actions = data.get("key_actions", [])
        participants = data.get("participants", [])
        call_id = data.get("call_id")

        # Normalize action items to consistent structure
        normalized_actions = []
        for action in key_actions:
            if isinstance(action, str):
                # Simple string format: "Task description"
                normalized_actions.append({
                    "task_title": action,
                    "owner_name": None,
                    "owner_email": None,
                    "due_date": None
                })
            elif isinstance(action, dict):
                # Dict format: could have various field names
                # Handle both "description" (from webhook) and "task_title" (normalized)
                task_title = (
                    action.get("description") or 
                    action.get("task_title") or 
                    action.get("title") or 
                    "Untitled Task"
                )
                
                owner_name = (
                    action.get("owner_name") or 
                    action.get("owner") or 
                    action.get("assignee", {}).get("name") if isinstance(action.get("assignee"), dict) else None
                )
                
                owner_email = (
                    action.get("owner_email") or
                    action.get("assignee", {}).get("email") if isinstance(action.get("assignee"), dict) else None
                )
                
                normalized_actions.append({
                    "task_title": task_title,
                    "owner_name": owner_name,
                    "owner_email": owner_email,
                    "due_date": action.get("due_date"),
                    "timestamp": action.get("timestamp"),
                    "playback_url": action.get("playback_url"),
                    "team": action.get("team")
                })
        
        # Normalize participants (if they exist)
        normalized_participants = []
        for participant in participants:
            if isinstance(participant, str):
                normalized_participants.append({
                    "name": participant,
                    "email": None,
                    "is_external": False
                })
            elif isinstance(participant, dict):
                normalized_participants.append({
                    "name": participant.get("name"),
                    "email": participant.get("email"),
                    "is_external": participant.get("is_external", False),
                    "domain": participant.get("domain")
                })
        
        return {
            'status': 'success',
            'call_id': call_id,
            'things_discussed': things_discussed,
            'key_actions': normalized_actions,
            'participants': normalized_participants if normalized_participants else participants
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': f'Failed to parse summary: {str(e)}'
        }