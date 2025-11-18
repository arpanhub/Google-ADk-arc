from notion_client import Client
import os

client = Client(auth=os.getenv("NOTION_API_KEY"))

def delete_notion_page(page_id):
    """
    Delete a Notion page by archiving it.
    Args:
        page_id: ID of the Notion page to delete
    Returns:
        bool: True if deletion (archival) was successful, False otherwise
    """
    result = client.pages.update(
        page_id=page_id,
        archived=True
    )
    return result["archived"]  # Returns True if successful
