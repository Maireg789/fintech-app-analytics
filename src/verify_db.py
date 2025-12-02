python
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import text
import os
from dotenv import load_dotenv

# Load Config
load_dotenv()
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

def verify_data():
    """Runs a suite of SQL checks to verify data integrity."""
    print("🕵️ Starting Database Verification...")
    
    try:
        engine = create_engine(f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
        conn = engine.connect()
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        return

    # TEST 1: Check Row Counts
    count = conn.execute(text("SELECT COUNT(*) FROM reviews;")).scalar()
    if count > 0:
        print(f"✅ PASS: Data exists ({count} reviews found).")
    else:
        print("❌ FAIL: Reviews table is empty.")

    # TEST 2: Check Referential Integrity (Orphans)
    orphans = conn.execute(text("SELECT COUNT(*) FROM reviews WHERE bank_id NOT IN (SELECT bank_id FROM banks);")).scalar()
    if orphans == 0:
        print("✅ PASS: Referential Integrity maintained (No orphan reviews).")
    else:
        print(f"❌ FAIL: Found {orphans} reviews with invalid bank_ids.")

    # TEST 3: Check Sentiment Validity
    invalid_sentiments = conn.execute(text("SELECT COUNT(*) FROM reviews WHERE sentiment_label NOT IN ('POSITIVE', 'NEGATIVE', 'NEUTRAL');")).scalar()
    if invalid_sentiments == 0:
        print("✅ PASS: All sentiment labels are valid.")
    else:
        print(f"❌ FAIL: Found {invalid_sentiments} rows with invalid sentiment labels.")

    conn.close()
    print("🏁 Verification Complete.")

if __name__ == "__main__":
    verify_data()