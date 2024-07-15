import time
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import SerpData, db
from app import create_app
from fetch_serp import fetch_serp

# Create the Flask app and set up the database
app = create_app()
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
Session = sessionmaker(bind=engine)
session = Session()

def check_and_update_serp():
    while True:
        # Query the database for entries with blank serp_page
        entries = session.query(SerpData).filter(SerpData.serp_page == '').all()
        
        for entry in entries:
            domain = entry.domain
            serp_data = fetch_serp(domain)
            
            # Update the entry with the fetched SERP data
            entry.serp_page = serp_data
            entry.time = datetime.now(timezone.utc)
            session.commit()
        
        # Sleep for a specified interval before checking again
        time.sleep(60)  # Check every 60 seconds

if __name__ == '__main__':
    check_and_update_serp()