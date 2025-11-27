import pandas as pd
import os
from transformers import pipeline
from sklearn.feature_extraction.text import CountVectorizer

# Import the upgraded tools
from preprocess import clean_text, data_quality_report, clean_dataframe

INPUT_FILE = 'data/raw/raw_reviews.csv'
OUTPUT_FILE = 'data/processed/analyzed_reviews.csv'

def load_and_clean_data():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return None
    
    df = pd.read_csv(INPUT_FILE)
    
    # --- ADDRESSING FEEDBACK HERE ---
    # Apply strict cleaning (Deduplication, Dates, Missingness)
    df = clean_dataframe(df)
    
    # Run Quality Check
    data_quality_report(df)
    
    # Create temp column for NLP
    df['clean_content'] = df['content'].apply(clean_text)
    
    return df

def analyze_sentiment(df):
    print("Running Sentiment Analysis (DistilBERT)...")
    try:
        sentiment_pipeline = pipeline(
            "sentiment-analysis", 
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )
        
        def get_sentiment(text):
            try:
                # Truncate to 512 tokens
                result = sentiment_pipeline(str(text)[:512])[0]
                return result['label'], result['score']
            except:
                return "NEUTRAL", 0.5

        df[['sentiment_label', 'sentiment_score']] = df['content'].apply(
            lambda x: pd.Series(get_sentiment(x))
        )
    except Exception as e:
        print(f"Sentiment Model Error: {e}")
    return df

def extract_keywords(df):
    print("Extracting Data-Driven Themes...")
    
    custom_stop_words = ['the', 'and', 'to', 'is', 'it', 'for', 'of', 'in', 'app', 'bank', 'ethiopia', 'my', 'mobile', 'banking', 'please']
    
    try:
        vectorizer = CountVectorizer(stop_words='english', max_features=10)
        
        def get_top_keywords(subset_df):
            # Safety check for empty or all-whitespace data
            if subset_df.empty or subset_df['clean_content'].str.strip().eq("").all():
                return "None"
            try:
                vectorizer.fit(subset_df['clean_content'])
                return ", ".join(vectorizer.get_feature_names_out())
            except ValueError:
                return "Insufficient Data"

        print("\n--- INSIGHTS: Top Pain Points (Keywords in Negative Reviews) ---")
        neg_reviews = df[df['sentiment_label'] == 'NEGATIVE']
        
        for bank in df['bank_name'].unique():
            bank_neg = neg_reviews[neg_reviews['bank_name'] == bank]
            keywords = get_top_keywords(bank_neg)
            print(f"[{bank}]: {keywords}")
        print("----------------------------------------------------------------\n")
        
    except Exception as e:
        print(f"Keyword Extraction Warning: {e}")

    # Rule-Based tagging
    def consistent_theme(text):
        t = str(text).lower()
        if any(w in t for w in ['login', 'otp', 'sms', 'code', 'sign', 'account']): return "Authentication"
        if any(w in t for w in ['slow', 'stuck', 'load', 'wait', 'connect']): return "Performance"
        if any(w in t for w in ['crash', 'close', 'bug', 'error', 'failed']): return "Stability"
        if any(w in t for w in ['trans', 'pay', 'send', 'telebirr']): return "Transactions"
        return "General"
    
    df['theme'] = df['content'].apply(consistent_theme)
    return df

if __name__ == "__main__":
    df = load_and_clean_data()
    if df is not None:
        df = analyze_sentiment(df)
        df = extract_keywords(df)
        
        os.makedirs('data/processed', exist_ok=True)
        # Clean up columns before saving
        if 'clean_content' in df.columns:
            df = df.drop(columns=['clean_content'])
            
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"Success. Analyzed data saved to {OUTPUT_FILE}")