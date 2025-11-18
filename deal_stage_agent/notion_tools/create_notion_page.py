from notion_client import Client
import os

notion = Client(auth=os.getenv("NOTION_API_KEY"))

def create_notion_page(parent_page_id, title="Sample Page", blocks=None):
    children = blocks if blocks else []
    new_page = notion.pages.create(
        parent={"page_id": parent_page_id},
        properties={
            "title": {
                "title": [
                    {"text": {"content": title}}
                ]
            }
        },
        children=children
    )
    return new_page['id']
