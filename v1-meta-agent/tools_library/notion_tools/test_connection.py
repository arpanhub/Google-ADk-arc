from notion_client import Client

# Initialize the client with your integration token
notion = Client(auth="")

# Test the connection
try:
    me = notion.users.me()
    print("Connection successful!")
    print(f"Bot ID: {me['id']}")
except Exception as e:
    print(f"Connection failed: {e}")
