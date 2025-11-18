"""
Appends content to an existing Notion page
"""
import os
from notion_client import Client
from typing import Dict, Any


def append_to_notion_page(page_id: str, content: str) -> Dict[str, Any]:
    """
    Appends content to an existing Notion page.
    
    Args:
        page_id: Notion page ID (32 character string)
        content: Content to append in plain text
    
    Returns:
        dict: Result with success status
    """
    notion_api_key = os.getenv("NOTION_API_KEY")
    if not notion_api_key:
        return {"error": "NOTION_API_KEY not found in environment variables"}
    
    client = Client(auth=notion_api_key)
    
    try:
        blocks = [{
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": content}}]
            }
        }]
        
        response = client.blocks.children.append(
            block_id=page_id,
            children=blocks
        )
        
        print(f"✅ Appended content to Notion page {page_id}")
        return {
            "success": True,
            "page_id": page_id
        }
        
    except Exception as e:
        print(f"❌ Error appending to Notion page: {e}")
        return {"error": str(e)}