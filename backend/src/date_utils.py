from datetime import datetime

def parse_datetime_string(datetime_str):
    """
    Parses a date/time coming from the frontend in local time.
    Frontend sends: '2025-10-07T14:30:00.000'
    We parse it as naive datetime (without timezone info) to preserve local time
    """
    if not datetime_str:
        return None
    
    try:
        if datetime_str.endswith('Z'):
            datetime_str = datetime_str[:-1]
        
        if '.' in datetime_str:
            return datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%f')
        else:
            return datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S')
    except Exception as e:
        print(f"⚠️ Error parsing date '{datetime_str}': {e}")
        return None

def datetime_to_string(dt):
    """
    Converts a datetime object to ISO format string without timezone conversion.
    Returns: '2025-10-07T14:30:00.000'
    """
    if not dt:
        return None
    
    if isinstance(dt, str):
        return dt
    
    # Format without Z (which would indicate UTC)
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]