"""
Process user-provided Fathom payload tool
"""
import json
from typing import Dict, Any
from .receive_fathom_webhook import receive_fathom_webhook


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
