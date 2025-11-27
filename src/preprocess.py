import re
import pandas as pd
import numpy as np

def clean_text(text):
    """
    Standardizes text for keyword extraction.
    """
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r'[^a-z\s]', '', text) # Keep only letters
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def clean_dataframe(df):
    """
    Performs strict data cleaning (Deduplication, Missingness, Dates).
    Addressed Feedback: Explicit cleaning steps.
    """
    initial_count = len(df)
    print(f"Raw data count: {initial_count}")

    # 1. MISSINGNESS ENFORCEMENT
    # Drop rows where critical info is missing
    # We need 'content' for NLP, 'score' for stats, 'at' for time series
    df = df.dropna(subset=['content', 'score', 'at'])
    print(f"Dropped {initial_count - len(df)} rows with missing values.")

    # 2. DEDUPLICATION
    # Drop exact duplicates (same user text for the same bank)
    # keeping 'first' occurrence
    before_dedup = len(df)
    df = df.drop_duplicates(subset=['content', 'bank_name'], keep='first')
    print(f"Dropped {before_dedup - len(df)} duplicate reviews.")

    # 3. STRICT DATE NORMALIZATION
    # Convert 'at' to datetime objects
    df['at'] = pd.to_datetime(df['at'], errors='coerce')
    
    # Drop rows where date conversion failed (if any)
    df = df.dropna(subset=['at'])
    
    # Sort by date (good practice)
    df = df.sort_values(by='at', ascending=False)

    print(f"Final clean count: {len(df)}")
    return df

def data_quality_report(df):
    """
    Prints a summary of the dataset health.
    """
    print("\n=== DATA QUALITY REPORT ===")
    print(f"Total Rows: {len(df)}")
    
    # Check for remaining missing values
    missing = df.isnull().sum()
    if missing.sum() > 0:
        print("Warning: Missing Values remaining:")
        print(missing[missing > 0])
    else:
        print("Missing Values: 0 (Passed)")
        
    # Check Date Range
    if 'at' in df.columns:
        print(f"Date Range: {df['at'].min()} to {df['at'].max()}")

    print("===========================\n")
    return df