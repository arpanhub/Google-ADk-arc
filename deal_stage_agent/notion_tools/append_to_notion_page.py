import os
from notion_client import Client

client = Client(auth=os.getenv("NOTION_API_KEY"))

def append_to_notion_page(page_id, blocks):
    """
    Append content blocks to an existing Notion page.
    Args:
        token: Notion integration token
        page_id: ID of the Notion page to append to
        blocks: List of content blocks to append
    blocks = [
    {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {"text": {"content": "Appended content!"}}
            ]
        }
    }
]
    Returns:
        dict: Response from Notion API  
    """
    response = client.blocks.children.append(
        block_id=page_id,
        children=blocks
    )
    return response
