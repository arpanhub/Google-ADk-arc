"""
Creates a new page in Notion workspace
"""
import os
from notion_client import Client
from typing import Dict, Any


def create_page(parent_id: str, title: str, content: str = "") -> Dict[str, Any]:
    """
    Creates a new page in Notion workspace.
    
    Args:
        parent_id: Parent page or database ID (32 character string)
        title: Page title
        content: Page content in plain text (optional)
    
    Returns:
        dict: Created page object with id and url
    """
    notion_api_key = os.getenv("NOTION_API_KEY")
    if not notion_api_key:
        return {"error": "NOTION_API_KEY not found in environment variables"}
    
    client = Client(auth=notion_api_key)
    
    try:
        properties = {
            "title": {
                "title": [{"text": {"content": title}}]
            }
        }
        
        children = []
        if content:
            children.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": content}}]
                }
            })
        
        new_page = client.pages.create(
            parent={"page_id": parent_id},
            properties=properties,
            children=children if children else None
        )
        
        print(f"✅ Created Notion page: {new_page['url']}")
        return {
            "success": True,
            "page_id": new_page["id"],
            "url": new_page["url"]
        }
        
    except Exception as e:
        print(f"❌ Error creating Notion page: {e}")
        return {"error": str(e)}