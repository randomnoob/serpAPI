from datetime import datetime, timezone, timedelta
import json

# Vietnamese translations
weekday_names_vi = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
month_names_vi = ["Tháng Một", "Tháng Hai", "Tháng Ba", "Tháng Tư", "Tháng Năm", "Tháng Sáu",
                  "Tháng Bảy", "Tháng Tám", "Tháng Chín", "Tháng Mười", "Tháng Mười Một", "Tháng Mười Hai"]

def format_datetime_vietnamese(utc_datetime):
    # Get components of the datetime
    year = utc_datetime.year
    month = utc_datetime.month
    day = utc_datetime.day
    hour = utc_datetime.hour
    minute = utc_datetime.minute
    second = utc_datetime.second
    
    # Translate weekday and month names
    weekday_vi = weekday_names_vi[utc_datetime.weekday()]
    month_vi = month_names_vi[month - 1]  # Month names are 0-indexed in Python
    
    # Format datetime string in Vietnamese
    vietnamese_datetime_str = f"{weekday_vi}, {day} {month_vi} {year} {hour}:{minute}:{second}"
    
    return vietnamese_datetime_str


def has_24_hours_passed(time1, time2):
    """
    Check if 24 hours have passed between two datetime objects.
    
    Parameters:
    - time1 (datetime): The first datetime object.
    - time2 (datetime): The second datetime object.
    
    Returns:
    - bool: True if 24 hours have passed between the two datetime objects, False otherwise.
    """
    # Ensure both datetime objects are timezone-aware or timezone-naive
    if time1.tzinfo != time2.tzinfo:
        raise ValueError("Both datetime objects must have the same timezone information")
    
    # Calculate the time difference
    time_difference = abs(time2 - time1)
    
    # Check if the time difference is 24 hours or more
    return time_difference >= timedelta(hours=24)


def get_hanoi_current_time():
    return datetime.now(timezone.utc) + timedelta(hours=7)


def convert_to_hanoi_time(utc_datetime):
    # Define the GMT+7 timezone offset
    gmt7_offset = timedelta(hours=7)
    
    # Convert the UTC datetime to GMT+7 by adding the offset
    gmt7_datetime = utc_datetime + gmt7_offset
    
    # Set the timezone information to GMT+7
    gmt7_datetime = gmt7_datetime.replace(tzinfo=timezone(timedelta(hours=7)))
    
    return gmt7_datetime


def serper_check_top1_match(serper_response, comparison_string):
    try:
        if isinstance(serper_response, str):
            serper_response = json.loads(serper_response)
        position_1_element = next((item for item in serper_response['organic'] if item['position'] == 1), None)
        print(f"Element 1 link: {position_1_element['link']}")
        if position_1_element['link'] == comparison_string:
            return True
        return False
    except Exception as e:
        return False