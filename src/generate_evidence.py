import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# CONFIGURATION
INPUT_FILE = 'data/processed/analyzed_reviews.csv'
OUTPUT_DIR = 'reports/figures'

def generate_evidence():
    # 1. Load Data
    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: {INPUT_FILE} not found. Please run 'python src/analysis.py' first.")
        return

    df = pd.read_csv(INPUT_FILE)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("\n" + "="*50)
    print("      DATA FOR YOUR REPORT (COPY THESE TABLES)")
    print("="*50)

    # --- TABLE 1: SENTIMENT DISTRIBUTION ---
    print("\n>>> TABLE 1: Sentiment Distribution (%)")
    # Calculate percentages
    sentiment_pct = pd.crosstab(df['bank_name'], df['sentiment_label'], normalize='index') * 100
    sentiment_pct = sentiment_pct.round(1) # Round to 1 decimal place
    print(sentiment_pct)

    # --- FIGURE 1: SENTIMENT CHART ---
    # FIX: Safer calculation method to avoid "ValueError"
    plt.figure(figsize=(8, 5))
    
    # 1. Count sentiments per bank
    counts = df.groupby(['bank_name', 'sentiment_label']).size().reset_index(name='count')
    # 2. Count total reviews per bank
    totals = df.groupby('bank_name').size().reset_index(name='total')
    # 3. Merge and calculate percentage
    df_chart = counts.merge(totals, on='bank_name')
    df_chart['percentage'] = (df_chart['count'] / df_chart['total']) * 100
    
    sns.barplot(x='bank_name', y='percentage', hue='sentiment_label', data=df_chart, 
                palette={'POSITIVE': 'green', 'NEUTRAL': 'gray', 'NEGATIVE': 'red'})
    plt.title('Sentiment Distribution by Bank')
    plt.ylabel('Percentage (%)')
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/figure1_sentiment.png")
    print(f"\n[Check Created]: Figure 1 saved to {OUTPUT_DIR}/figure1_sentiment.png")

    # --- TABLE 2: TOP PAIN POINTS (Thematic Analysis) ---
    print("\n>>> TABLE 2: Top Pain Points (Negative Reviews Only)")
    neg_df = df[df['sentiment_label'] == 'NEGATIVE']
    
    if not neg_df.empty:
        # Count specific themes per bank
        pain_points = neg_df.groupby(['bank_name', 'theme']).size().unstack(fill_value=0)
        print(pain_points)

        # --- FIGURE 2: PAIN POINTS CHART ---
        plt.figure(figsize=(10, 6))
        sns.countplot(x='theme', hue='bank_name', data=neg_df, palette='magma')
        plt.title('Key Pain Points (Count of Negative Reviews)')
        plt.xlabel('Theme')
        plt.ylabel('Number of Complaints')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"{OUTPUT_DIR}/figure2_pain_points.png")
        print(f"\n[Check Created]: Figure 2 saved to {OUTPUT_DIR}/figure2_pain_points.png")
    else:
        print("No negative reviews found. Skipping Figure 2.")
        
    print("="*50 + "\n")

if __name__ == "__main__":
    generate_evidence()