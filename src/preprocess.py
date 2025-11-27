import re
import pandas as pd

def clean_text(text):
    """
    Standardizes text for keyword extraction.
    - Lowercase
    - Removes punctuation/numbers (keep only words)
    - Removes extra whitespace
    """
    if pd.isna(text):
        return ""
    
    text = str(text).lower()
    
    # Remove emojis and special chars (keep only a-z and spaces)
    # This helps the keyword extractor focus on words
    text = re.sub(r'[^a-z\s]', '', text)
    
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def data_quality_report(df):
    """
    Explicit Data Quality Checks.
    Prints a summary of the dataset health.
    """
    print("\n=== DATA QUALITY REPORT ===")
    print(f"Total Rows: {len(df)}")
    
    # Check for duplicates
    dupes = df.duplicated(subset=['content']).sum()
    print(f"Duplicate Reviews: {dupes} ({(dupes/len(df))*100:.1f}%)")
    
    # Check for missing values
    missing = df.isnull().sum()
    if missing.sum() > 0:
        print("Missing Values per Column:")
        print(missing[missing > 0])
    else:
        print("No Missing Values found.")
        
    # Check for short/spam reviews
    short_reviews = df[df['content'].str.len() < 10].shape[0]
    print(f"Short/Spam Reviews (<10 chars): {short_reviews}")
    print("===========================\n")
    
    return df