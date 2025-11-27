import pandas as pd
import numpy as np
from transformers import pipeline
import os

# CONFIGURATION
INPUT_FILE = 'data/raw/raw_reviews.csv'
OUTPUT_FILE = 'data/processed/analyzed_reviews.csv'

def load_data():
    """Load raw data and handle basic cleaning."""
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found. Please run src/scraper.py first.")
        return None
    
    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df)} raw reviews.")
    
    # Drop rows where content is empty/NaN
    df = df.dropna(subset=['content'])
    
    # Ensure content is string type
    df['content'] = df['content'].astype(str)
    
    return df

def analyze_sentiment_bert(df):
    """
    Uses a pre-trained BERT model to score sentiment (Positive/Negative).
    Model: distilbert-base-uncased-finetuned-sst-2-english
    """
    print("\n--- Starting Sentiment Analysis (This may take time) ---")
    print("Loading AI Model...")
    
    try:
        # Initialize the pipeline
        sentiment_pipeline = pipeline(
            "sentiment-analysis", 
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )
    except Exception as e:
        print(f"Error loading model: {e}")
        return df

    print("Analyzing reviews... (Please wait)")
    
    # Helper function to process single text
    def get_sentiment(text):
        # Truncate to 512 tokens to fit model limits
        text = text[:512]
        try:
            result = sentiment_pipeline(text)[0]
            return result['label'], result['score']
        except:
            return "NEUTRAL", 0.5

    # Apply to DataFrame
    # Using zip to unpack the tuple into two columns
    df[['sentiment_label', 'sentiment_score']] = df['content'].apply(
        lambda x: pd.Series(get_sentiment(x))
    )
    
    print("Sentiment Analysis Complete.")
    return df

def assign_theme(df):
    """
    Categorizes reviews based on keywords.
    """
    print("\n--- Starting Thematic Analysis ---")
    
    def get_theme(text):
        text = text.lower()
        
        # Priority 1: Authentication (Critical Pain Point)
        if any(x in text for x in ['login', 'sign in', 'password', 'otp', 'sms', 'code', 'fingerprint', 'face id', 'register']):
            return 'Authentication & Security'
            
        # Priority 2: Technical Stability
        elif any(x in text for x in ['crash', 'bug', 'close', 'stopped', 'freeze', 'shut', 'error', 'open']):
            return 'App Stability (Bugs)'
            
        # Priority 3: Performance
        elif any(x in text for x in ['slow', 'lag', 'hang', 'wait', 'loading', 'speed', 'fast']):
            return 'Performance/Speed'
            
        # Priority 4: Features & Transactions
        elif any(x in text for x in ['transfer', 'send', 'pay', 'transaction', 'recharge', 'airtime', 'statement']):
            return 'Transactions & Features'
            
        # Priority 5: UX/UI
        elif any(x in text for x in ['ui', 'design', 'interface', 'look', 'user friendly', 'easy', 'app', 'update']):
            return 'User Interface (UI)'
            
        # Fallback
        return 'General Feedback'

    df['theme'] = df['content'].apply(get_theme)
    print("Themes Assigned.")
    return df

if __name__ == "__main__":
    # 1. Load
    df = load_data()
    
    if df is not None:
        # 2. Analyze Sentiment
        df = analyze_sentiment_bert(df)
        
        # 3. Analyze Themes
        df = assign_theme(df)
        
        # 4. Save
        os.makedirs('data/processed', exist_ok=True)
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"\nSUCCESS! Processed {len(df)} reviews.")
        print(f"Saved to: {OUTPUT_FILE}")
        
        # Preview
        print("\nSample Data:")
        print(df[['content', 'sentiment_label', 'theme']].head())