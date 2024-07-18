import time
import json
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import SerpData
from get_serp import get_serp
from get_serp_serper import get_serp_serper
from config import SQLALCHEMY_DATABASE_URI
from utils import has_24_hours_passed, get_hanoi_current_time\
                , convert_to_hanoi_time, serper_check_top1_match

engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

def update_serp(entries, session):
    # Get SERP and update entries in the DB
    for entry in entries:
        url = entry.url
        # serp_data = get_serp(url)
        serper_options = {
            "location": "Vietnam",
            "gl": "vn",
            "hl": "vi"
        }
        serp_data = get_serp_serper(url)
        
        serp_data_raw = json.dumps(serp_data)
        
        # Update the entry with the fetched SERP data and the current timestamp
        entry.serp_page = serp_data_raw
        entry.time = get_hanoi_current_time()
        entry.top1_match = serper_check_top1_match(serp_data, url)

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




def get_old_entries():
    notblank_objects = session.query(SerpData).filter(SerpData.serp_page != '').all()
    # Get the current time
    current_time = get_hanoi_current_time()

    obsolete_entries_queue = []
    for entry in notblank_objects:
        db_timestamp = entry.time
        db_timestamp = convert_to_hanoi_time(db_timestamp)
        # Check if 24 hours have passed
        has_passed = has_24_hours_passed(db_timestamp, current_time)
        if has_passed:
            obsolete_entries_queue.append(entry)
    return obsolete_entries_queue


if __name__ == '__main__':
    poll_and_update_serp()