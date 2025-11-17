"""
Get current time tool
"""
from datetime import datetime


def get_current_time() -> str:
    """
    Gets the current date and time in ISO format.
    Useful for calculating due dates and reminder times.
    
    Returns:
        str: Current time in ISO format (YYYY-MM-DDTHH:MM:SS)
    
    Example:
        >>> current_time = get_current_time()
        >>> print(current_time)
        "2025-11-14T16:45:30"
    """
    now = datetime.now()
    iso_time = now.strftime("%Y-%m-%dT%H:%M:%S")
    print(f"⏰ Current time: {iso_time}")
    return iso_time
