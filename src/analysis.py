import pandas as pd
import os
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from transformers import pipeline
from sklearn.feature_extraction.text import CountVectorizer

# Import from your corrected preprocess file
from preprocess import clean_text, data_quality_report, clean_dataframe

INPUT_FILE = 'data/raw/raw_reviews.csv'
OUTPUT_FILE = 'data/processed/analyzed_reviews.csv'

# --- NLTK SETUP (Stable Lemmatization) ---
print("Setting up NLTK...")
try:
    nltk.data.find('corpora/wordnet')
    nltk.data.find('corpora/stopwords')
except LookupError:
    print("Downloading NLTK data...")
    nltk.download('wordnet')
    nltk.download('omw-1.4')
    nltk.download('stopwords')

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def load_and_clean_data():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return None
    
    df = pd.read_csv(INPUT_FILE)
    
    # 1. Use your strict cleaning function
    df = clean_dataframe(df)
    data_quality_report(df)
    
    # 2. Basic Text Cleaning
    df['clean_content'] = df['content'].apply(clean_text)
    
    # --- REQUIREMENT: DEEP PREPROCESSING (Lemmatization) ---
    print("Applying NLTK Lemmatization...")
    
    def lemmatize_text(text):
        if not isinstance(text, str): return ""
        # Split text into words
        words = text.split()
        # Lemmatize (run -> run, running -> run)
        lemmas = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]
        return " ".join(lemmas)

    # We store this in a new column for the theme analysis
    df['lemmatized_content'] = df['clean_content'].apply(lemmatize_text)
    
    return df

def analyze_sentiment(df):
    print("Running Sentiment Analysis...")
    try:
        sentiment_pipeline = pipeline(
            "sentiment-analysis", 
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )
        
        def get_sentiment(text):
            try:
                # Truncate to 512 tokens to prevent crashes
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
    print("Extracting Themes...")
    
    # --- REQUIREMENT: RICHER CLUSTERING ---
    # We use the LEMMATIZED column to group similar words together
    def consistent_theme(text):
        t = str(text).lower()
        
        # Authentication Cluster
        if any(w in t for w in ['login', 'otp', 'sms', 'code', 'sign', 'account', 'password', 'verify', 'log']): 
            return "Authentication"
        
        # Performance Cluster
        if any(w in t for w in ['slow', 'stuck', 'load', 'wait', 'connect', 'lag', 'hang', 'freeze']): 
            return "Performance"
        
        # Stability Cluster (Bug/Crash)
        if any(w in t for w in ['crash', 'close', 'bug', 'error', 'fail', 'shut', 'glitch']): 
            return "Stability"
        
        # Transactions Cluster
        if any(w in t for w in ['trans', 'pay', 'send', 'telebirr', 'transfer', 'money', 'deposit']): 
            return "Transactions"
        
        # UI/UX Cluster
        if any(w in t for w in ['ui', 'design', 'interface', 'look', 'color', 'screen', 'easy', 'hard']): 
            return "User Experience"
            
        return "General"
    
    df['theme'] = df['lemmatized_content'].apply(consistent_theme)
    return df

if __name__ == "__main__":
    df = load_and_clean_data()
    if df is not None:
        df = analyze_sentiment(df)
        df = extract_keywords(df)
        
        os.makedirs('data/processed', exist_ok=True)
        
        # Save the file
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"Success! Data saved to {OUTPUT_FILE}")