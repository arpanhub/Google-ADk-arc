"""
Calculate future time tool
"""
from datetime import datetime, timedelta


def calculate_future_time(base_time: str, add_minutes: int) -> str:
    """
    Calculates a future time by adding minutes to a base time.
    
    Args:
        base_time: Base time in ISO format (YYYY-MM-DDTHH:MM:SS)
        add_minutes: Number of minutes to add
    
    Returns:
        str: Future time in ISO format
    
    Example:
        >>> future = calculate_future_time("2025-11-14T16:45:30", 2)
        >>> print(future)
        "2025-11-14T16:47:30"
    """
    try:
        if 'T' in base_time:
            base_dt = datetime.fromisoformat(base_time)
        else:
            base_dt = datetime.strptime(base_time, "%Y-%m-%d %H:%M:%S")
        
        future_dt = base_dt + timedelta(minutes=add_minutes)
        future_time = future_dt.strftime("%Y-%m-%dT%H:%M:%S")
        
        print(f"📅 Base time: {base_time}")
        print(f"➕ Adding {add_minutes} minutes")
        print(f"🎯 Result: {future_time}")
        
        return future_time
    except Exception as e:
        print(f"❌ Error calculating future time: {str(e)}")
        return ""
