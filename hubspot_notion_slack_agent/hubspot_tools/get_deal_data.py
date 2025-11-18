from hubspot import HubSpot
import os

client = HubSpot(api_key=os.getenv("HUBSPOT_API_KEY"))

def get_deal_data(deal_id):
    """
    Retrieve deal data from HubSpot by deal ID.
    
    Args:
        deal_id (str): The ID of the deal to retrieve.
    Returns:
        dict: Deal data if found, else empty dict.
    """
    try:
        deal = client.deals.get_by_id(deal_id)
        return deal
    except Exception as e:
        print(f"Error retrieving deal {deal_id}: {e}")
        return {}
# Example usage:
# deal_info = get_deal_data("123456")
# print(deal_info)