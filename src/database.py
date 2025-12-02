import pandas as pd
from sqlalchemy import create_engine
import os
import logging
from dotenv import load_dotenv

# 1. SETUP LOGGING
# We use encoding='utf-8' for the file to handle special characters safely
# We removed emojis from the console output to prevent Windows crashes
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 2. LOAD CONFIGURATION
load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

# Check if password loaded correctly
if not DB_PASS:
    logging.error("[CRITICAL] DB_PASS not found. Please make sure the .env file is SAVED.")
    exit()

# 3. CONNECT TO DATABASE
try:
    connection_str = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    engine = create_engine(connection_str)
    logging.info("[INFO] Database connection established.")
except Exception as e:
    logging.critical(f"[CRITICAL] Failed to connect to DB: {e}")
    exit()

# 4. LOAD DATA
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_dir, '..', 'data', 'processed', 'analyzed_reviews.csv')

if not os.path.exists(csv_path):
    csv_path = 'data/processed/analyzed_reviews.csv'

try:
    df = pd.read_csv(csv_path)
    logging.info(f"[INFO] Loaded {len(df)} rows from CSV.")
except FileNotFoundError:
    logging.error(f"[ERROR] Could not find file at: {csv_path}")
    exit()

# 5. INSERT BANKS (Dimension Table)
banks_data = pd.DataFrame({
    'bank_name': ['Commercial Bank of Ethiopia', 'Bank of Abyssinia', 'Dashen Bank'],
    'app_name': ['CBE Mobile', 'BoA Mobile', 'Amole'] 
})

try:
    banks_data.to_sql('banks', engine, if_exists='append', index=False)
    logging.info("[SUCCESS] Banks table populated (or already existed).")
except Exception as e:
    logging.warning(f"[INFO] Banks table skip: {e}")

# 6. SMART MAPPING LOGIC
existing_banks = pd.read_sql("SELECT * FROM banks", engine)
db_map = dict(zip(existing_banks['bank_name'], existing_banks['bank_id']))

custom_map = {
    'CBE': 'Commercial Bank of Ethiopia',
    'Commercial Bank of Ethiopia Mobile': 'Commercial Bank of Ethiopia',
    'CBE Mobile': 'Commercial Bank of Ethiopia',
    'BOA': 'Bank of Abyssinia',
    'BoA': 'Bank of Abyssinia',
    'Bank of Abyssinia Mobile': 'Bank of Abyssinia',
    'Dashen': 'Dashen Bank',
    'Amole': 'Dashen Bank',
    'Dashen Bank Sc': 'Dashen Bank'
}

def get_bank_id(row_val):
    if row_val in db_map:
        return db_map[row_val]
    if row_val in custom_map:
        clean_name = custom_map[row_val]
        return db_map.get(clean_name)
    return None

logging.info("[INFO] Mapping bank names...")

if 'bank_name' in df.columns:
    df['bank_id'] = df['bank_name'].apply(get_bank_id)
else:
    logging.error("[CRITICAL] 'bank_name' column missing.")
    exit()

# 7. CLEAN AND INSERT REVIEWS (Fact Table)
df = df.rename(columns={
    'content': 'review_text',  
    'at': 'review_date',      
    'score': 'rating'         
})

df_final = df.dropna(subset=['bank_id'])

cols_to_push = ['bank_id', 'review_text', 'rating', 'review_date', 'sentiment_label', 'sentiment_score', 'source']
df_final = df_final[[c for c in cols_to_push if c in df_final.columns]]

try:
    df_final.to_sql('reviews', engine, if_exists='append', index=False)
    logging.info(f"[SUCCESS] Inserted {len(df_final)} reviews into PostgreSQL.")
except Exception as e:
    logging.error(f"[ERROR] Insert Failed: {e}")