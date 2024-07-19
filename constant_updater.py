import time
import json
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from models import SerpData
from get_serp import get_serp
from get_serp_serper import get_serp_serper
from config import SQLALCHEMY_DATABASE_URI
from utils import has_24_hours_passed, get_hanoi_current_time\
                , convert_to_hanoi_time, serper_check_top1_match

engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

def get_old_entries():
    # Get entries from the DB, compare it to see if 24 hours has passed and refresh the SERP=> update to DB
    notblank_objects = session.query(SerpData).filter(SerpData.serp_page != '').all()
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

def update_serp(entries, session):
    # Get SERP and update entries data to the DB
    for entry in entries:
        url = entry.url
        # serp_data = get_serp(url)
        serper_options = {
            "location": "Vietnam",
            "gl": "vn",
            "hl": "vi"
        }
        serp_data = get_serp_serper(url, **serper_options)
        
        serp_data_raw = json.dumps(serp_data)
        
        # Update the entry with the fetched SERP data and the current timestamp
        entry.serp_page = serp_data_raw
        entry.time = get_hanoi_current_time()
        entry.top1_match = serper_check_top1_match(serp_data, url)
        session.commit()

def db_work(session, urls_to_update=None):
    if urls_to_update:
        entries = session.query(SerpData).filter(SerpData.url.in_(urls_to_update)).all()
        print(f"Update SOME urls only: {urls_to_update}")
    else:
        # Query the database for entries with blank serp_page
        entries = session.query(SerpData).filter(SerpData.serp_page == '').all()
        print(f"Update ALL BLANK SERP")
    # old_entries = get_old_entries()
    print(f"There is {len(entries)} entries to be updated")
    
    # Get SERP for the new, blank entries
    print("Get SERP for the new entries START")
    update_serp(entries, session)
    print("Get SERP for the new entries DONE")
    # Refresh SERP for old entries
    # print("Refresh SERP for old entries")
    # update_serp(old_entries, session)

def delete_some(session, urls_to_delete):
    entries = session.query(SerpData).filter(SerpData.url.in_(urls_to_delete)).all()
    for entry in entries:
        print(f"Delete {entry.url}")
        session.delete(entry)   
    session.commit()



@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()

def poll_and_update_serp():
    while True:
        with session_scope() as session:
            db_work(session)
        # Sleep for a specified interval before polling again
        time.sleep(60)  # Poll every 60 seconds

if __name__ == '__main__':
    poll_and_update_serp()