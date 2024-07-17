import time
import json
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import SerpData
from get_serp import get_serp
from config import SQLALCHEMY_DATABASE_URI

engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

def update_serp(entries, session):
    # Get SERP and update entries in the DB
    for entry in entries:
        url = entry.url
        serp_data = get_serp(url)
        serp_data_raw = json.dumps(serp_data)
        
        # Update the entry with the fetched SERP data and the current timestamp
        entry.serp_page = serp_data_raw
        entry.time = datetime.now(timezone.utc)
        session.commit()


def poll_and_update_serp():
    while True:
        # Query the database for entries with blank serp_page
        entries = session.query(SerpData).filter(SerpData.serp_page == '').all()
        old_entries = get_old_entries()
        print(f"There is {len(entries)} blank and {len(old_entries)} old entries")
        
        # Get SERP for the new, blank entries
        print("Get SERP for the new, blank entries")
        update_serp(entries, session)
        # Refresh SERP for old entries
        print("Refresh SERP for old entries")
        update_serp(old_entries, session)

        # Sleep for a specified interval before polling again
        time.sleep(60)  # Poll every 60 seconds
        print(f"Begin a new poll at {datetime.now(timezone.utc)}")


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

def get_old_entries():
    notblank_objects = session.query(SerpData).filter(SerpData.serp_page != '').all()
    # Get the current time
    current_time = datetime.now(timezone.utc)

    obsolete_entries_queue = []
    for entry in notblank_objects:
        db_timestamp = entry.time
        db_timestamp = db_timestamp.replace(tzinfo=timezone.utc)
        # Check if 24 hours have passed
        has_passed = has_24_hours_passed(db_timestamp, current_time)
        if has_passed:
            obsolete_entries_queue.append(entry)
    return obsolete_entries_queue


if __name__ == '__main__':
    poll_and_update_serp()