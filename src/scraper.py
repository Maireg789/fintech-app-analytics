import pandas as pd
from google_play_scraper import Sort, reviews
import time
import sys

# UPDATED APP IDs
APP_PACKAGES = {
    'CBE': 'com.combanketh.mobilebanking',
    'BOA': 'com.boa.boaMobileBanking',
    'Dashen': 'com.dashen.dashensuperapp'  # Updated to the new SuperApp
}

def scrape_reviews(bank_name, app_id, target_count=400):
    print(f"\n--- Starting scrape for {bank_name} ---")
    print(f"    App ID: {app_id}")
    
    all_reviews = []
    continuation_token = None
    
    # Retry logic
    max_retries = 3
    
    while len(all_reviews) < target_count:
        try:
            print(f"    Fetching batch... (Current count: {len(all_reviews)})")
            result, continuation_token = reviews(
                app_id,
                lang='en', 
                country='et', 
                sort=Sort.NEWEST, 
                count=200, 
                continuation_token=continuation_token
            )
            
            if not result:
                print(f"    No more reviews found for {bank_name}.")
                break
                
            all_reviews.extend(result)
            
            if len(all_reviews) >= target_count:
                break
            
            # Show user we are waiting
            print("    Waiting 1 second to avoid blocking...")
            time.sleep(1)
            
        except Exception as e:
            print(f"    ! Error scraping {bank_name}: {e}")
            break

    # SAFETY CHECK: If 0 reviews, return empty
    if not all_reviews:
        print(f"    WARNING: No reviews found for {bank_name}!")
        return pd.DataFrame()

    # Convert to DataFrame
    df = pd.DataFrame(all_reviews)
    
    # Check for missing columns (The source of your previous KeyError)
    required_cols = ['content', 'score', 'at', 'thumbsUpCount']
    available_cols = [c for c in required_cols if c in df.columns]
    
    if len(available_cols) < len(required_cols):
        print(f"    WARNING: Missing columns. Found: {df.columns}")
        # We proceed with whatever columns we have, filling missing ones
        for col in required_cols:
            if col not in df.columns:
                df[col] = None

    # Filter and Tag
    df = df[required_cols]
    df['bank_name'] = bank_name
    df['source'] = 'Google Play'
    df['review_id'] = [f"{bank_name}_{i}" for i in range(len(df))]
    
    print(f"    >>> Success: Collected {len(df)} reviews for {bank_name}")
    return df

if __name__ == "__main__":
    dfs = []
    print("Initializing Scraper...")
    
    for bank, app_id in APP_PACKAGES.items():
        df = scrape_reviews(bank, app_id, target_count=500)
        if not df.empty:
            dfs.append(df)
    
    if dfs:
        final_df = pd.concat(dfs, ignore_index=True)
        
        # Ensure directory exists
        import os
        os.makedirs('data/raw', exist_ok=True)
        
        save_path = 'data/raw/raw_reviews.csv'
        final_df.to_csv(save_path, index=False)
        print(f"\nDONE! Saved {len(final_df)} total reviews to '{save_path}'")
    else:
        print("\nFAILED: No data collected from any bank.")