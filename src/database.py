import pandas as pd
from sqlalchemy import create_engine
import os

# ---------------------------------------------------------
# 1. DATABASE CONNECTION SETUP
# ---------------------------------------------------------
DB_USER = 'postgres'
DB_PASS = '223027'       # Your Password
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'bank_reviews'

# Create connection engine
connection_str = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine = create_engine(connection_str)

print("🔌 Connecting to database...")

# ---------------------------------------------------------
# 2. LOAD DATA
# ---------------------------------------------------------
# Path logic to ensure we find the file
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_dir, '..', 'data', 'processed', 'analyzed_reviews.csv')

# Fallback path if running from root
if not os.path.exists(csv_path):
    csv_path = 'data/processed/analyzed_reviews.csv'

try:
    df = pd.read_csv(csv_path)
    print(f"✅ Loaded {len(df)} rows from CSV.")
except FileNotFoundError:
    print(f"❌ ERROR: Could not find file at: {csv_path}")
    exit()

# ---------------------------------------------------------
# 3. INSERT BANKS (Dimension Table)
# ---------------------------------------------------------
banks_data = pd.DataFrame({
    'bank_name': ['Commercial Bank of Ethiopia', 'Bank of Abyssinia', 'Dashen Bank'],
    'app_name': ['CBE Mobile', 'BoA Mobile', 'Amole'] 
})

try:
    banks_data.to_sql('banks', engine, if_exists='append', index=False)
    print("✅ Banks table populated.")
except Exception:
    print("ℹ️ Banks table might already have data. Continuing...")

# ---------------------------------------------------------
# 4. SMART MAPPING (CSV Names -> Database IDs)
# ---------------------------------------------------------
existing_banks = pd.read_sql("SELECT * FROM banks", engine)
db_map = dict(zip(existing_banks['bank_name'], existing_banks['bank_id']))

# Custom Map: Left = Your CSV Value | Right = Database Value
# This handles cases where your CSV says "CBE" but DB says "Commercial Bank of Ethiopia"
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
    # 1. Exact Match
    if row_val in db_map:
        return db_map[row_val]
    # 2. Custom Map
    if row_val in custom_map:
        clean_name = custom_map[row_val]
        return db_map.get(clean_name)
    return None

print("🔄 Mapping bank names to IDs...")

# We use the 'bank_name' column you confirmed exists
if 'bank_name' in df.columns:
    df['bank_id'] = df['bank_name'].apply(get_bank_id)
else:
    print("❌ CRITICAL ERROR: Could not find 'bank_name' column.")
    print(f"Columns found: {df.columns.tolist()}")
    exit()

# Check for unmapped rows
missing = df['bank_id'].isna().sum()
if missing > 0:
    print(f"⚠️ Warning: {missing} reviews could not be mapped to a bank ID and will be skipped.")

# ---------------------------------------------------------
# 5. PREPARE AND INSERT REVIEWS
# ---------------------------------------------------------
# Rename columns to match PostgreSQL Schema
df = df.rename(columns={
    'content': 'review_text',  
    'at': 'review_date',      # Your CSV has 'at', DB needs 'review_date'
    'score': 'rating'         # Your CSV has 'score', DB needs 'rating'
})

# Filter valid rows
df_final = df.dropna(subset=['bank_id'])

# Select columns that match the database table
cols_to_push = ['bank_id', 'review_text', 'rating', 'review_date', 'sentiment_label', 'sentiment_score', 'source']

# Only keep columns that actually exist in the dataframe
df_final = df_final[[c for c in cols_to_push if c in df_final.columns]]

# Insert
try:
    df_final.to_sql('reviews', engine, if_exists='append', index=False)
    print(f"🎉 SUCCESS! Inserted {len(df_final)} reviews into the database.")
except Exception as e:
    print(f"❌ Insert Failed: {e}")