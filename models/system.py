from datetime import datetime
from zoneinfo import ZoneInfo

def get_current_time(timezone: str = "UTC") -> str:
    """
    Get the current time including timezone.
    
    Args:
        timezone (str): IANA timezone string, e.g. "America/Edmonton", "Asia/Shanghai".
                        Defaults to "UTC".
    
    Returns:
        str: Current time with timezone in ISO format, e.g. "2025-09-01T16:07:24.191104-06:00".
    """
    now = datetime.now(ZoneInfo(timezone))
    return now.isoformat()

# Example usage:
print(get_current_time("America/Edmonton"))  # Calgary time
print(get_current_time("Asia/Shanghai"))     # Beijing time
print(get_current_time())                    # UTC time
