"""
Retrieves deal data from HubSpot CRM
"""
import os
from hubspot import HubSpot
from typing import Dict, Any


def get_deal_data(deal_id: str) -> Dict[str, Any]:
    """
    Retrieves deal data from HubSpot CRM by deal ID.
    
    Args:
        deal_id: HubSpot deal ID
    
    Returns:
        dict: Deal properties including amount, stage, close_date
    """
    hubspot_api_key = os.getenv("HUBSPOT_API_KEY")
    if not hubspot_api_key:
        return {"error": "HUBSPOT_API_KEY not found in environment variables"}
    
    client = HubSpot(api_key=hubspot_api_key)
    
    try:
        deal = client.deals.get_by_id(deal_id)
        
        print(f"Retrieved HubSpot deal: {deal_id}")
        return {
            "success": True,
            "deal_id": deal_id,
            "deal_data": deal
        }
        
    except Exception as e:
        print(f" Error retrieving deal {deal_id}: {e}")
        return {"error": str(e)}