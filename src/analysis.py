import pandas as pd
import os
from transformers import pipeline
from sklearn.feature_extraction.text import CountVectorizer
from preprocess import clean_text, data_quality_report
INPUT_FILE = 'data/raw/raw_reviews.csv'
OUTPUT_FILE = 'data/processed/analyzed_reviews.csv'

def load_and_clean_data():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return None
    
    df = pd.read_csv(INPUT_FILE)
    
    # 1. Run Data Quality Checks (Explicit robustness)
    data_quality_report(df)
    
    # 2. Preprocess for NLP
    # We keep 'content' raw for BERT (it understands context)
    # We create 'clean_content' for Keyword Extraction
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
            # Truncate to 512 for BERT limits
            try:
                result = sentiment_pipeline(text[:512])[0]
                return result['label'], result['score']
            except:
                return "NEUTRAL", 0.5

        df[['sentiment_label', 'sentiment_score']] = df['content'].apply(
            lambda x: pd.Series(get_sentiment(str(x)))
        )
    except Exception as e:
        print(f"Sentiment Model Error: {e}")
    return df

def extract_keywords(df):
    """
    Advanced Theme Extraction using Frequency Analysis.
    Finds top words in Negative reviews vs Positive reviews.
    """
    print("Extracting Data-Driven Themes...")
    
    # We use CountVectorizer to find top words, ignoring standard English stop words
    # plus common banking words that aren't helpful themes (like 'bank', 'app')
    custom_stop_words = ['the', 'and', 'to', 'is', 'it', 'for', 'of', 'in', 'app', 'bank', 'ethiopia', 'my']
    
    vectorizer = CountVectorizer(stop_words='english', max_features=10)
    
    def get_top_keywords(subset_df):
        if subset_df.empty: return "None"
        try:
            # Fit vectorizer to the clean text
            X = vectorizer.fit_transform(subset_df['clean_content'])
            # Get feature names (words)
            words = vectorizer.get_feature_names_out()
            return ", ".join(words)
        except ValueError:
            return "Insufficient Data"

    # Create a 'keywords' column based on the review's sentiment group
    # This is a simplified approach to tag the review with the top keywords of its cluster
    # For individual row tagging, we stick to rule-based for precision, 
    # but we PRINT the top keywords for the Report.
    
    print("\n--- INSIGHTS: Top Pain Points (Keywords in Negative Reviews) ---")
    neg_reviews = df[df['sentiment_label'] == 'NEGATIVE']
    for bank in df['bank_name'].unique():
        bank_neg = neg_reviews[neg_reviews['bank_name'] == bank]
        keywords = get_top_keywords(bank_neg)
        print(f"[{bank}]: {keywords}")
    print("----------------------------------------------------------------\n")

    # For the database, we stick to robust Rule-Based tagging because 
    # it is more consistent for SQL queries later.
    def consistent_theme(text):
        t = text.lower()
        if any(w in t for w in ['login', 'otp', 'sms', 'code', 'sign']): return "Authentication"
        if any(w in t for w in ['slow', 'stuck', 'load', 'wait']): return "Performance"
        if any(w in t for w in ['crash', 'close', 'bug', 'error']): return "Stability"
        if any(w in t for w in ['trans', 'pay', 'send', 'telebirr']): return "Transactions"
        return "General"
    
    df['theme'] = df['content'].apply(consistent_theme)
    return df

if __name__ == "__main__":
    df = load_and_clean_data()
    if df is not None:
        df = analyze_sentiment(df)
        df = extract_keywords(df)
        
        # Save
        os.makedirs('data/processed', exist_ok=True)
        # Drop the temp 'clean_content' column before saving to keep CSV clean
        df.drop(columns=['clean_content']).to_csv(OUTPUT_FILE, index=False)
        print(f"Success. Analyzed data saved to {OUTPUT_FILE}")