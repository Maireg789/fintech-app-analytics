import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from wordcloud import WordCloud
import os

# ---------------------------------------------------------
# 1. SETUP & DATA FETCHING
# ---------------------------------------------------------
DB_PASS = '223027'  # Your Password
engine = create_engine(f'postgresql://postgres:{DB_PASS}@localhost:5432/bank_reviews')

print("📊 Fetching data from PostgreSQL...")
query = """
SELECT r.review_text, r.rating, r.sentiment_label, b.bank_name
FROM reviews r
JOIN banks b ON r.bank_id = b.bank_id
"""
df = pd.read_sql(query, engine)

# Create output folder
if not os.path.exists('reports/figures'):
    os.makedirs('reports/figures')

# Set visual style
sns.set_theme(style="whitegrid")

# ------------------------------------------------------
# CHART 1: Sentiment Distribution by Bank
# ------------------------------------------------------
plt.figure(figsize=(10, 6))
# Order: Negative, Neutral, Positive
order = ['NEGATIVE', 'NEUTRAL', 'POSITIVE']
sns.countplot(data=df, x='bank_name', hue='sentiment_label', hue_order=order, palette='viridis')

plt.title('Customer Sentiment Distribution per Bank', fontsize=14, fontweight='bold')
plt.xlabel('Bank Name')
plt.ylabel('Number of Reviews')
plt.legend(title='Sentiment')
plt.tight_layout()
plt.savefig('reports/figures/sentiment_distribution.png')
print("✅ Saved chart: sentiment_distribution.png")

# ------------------------------------------------------
# CHART 2: Average Star Rating
# ------------------------------------------------------
plt.figure(figsize=(8, 5))
avg_rating = df.groupby('bank_name')['rating'].mean().reset_index()

sns.barplot(data=avg_rating, x='bank_name', y='rating', palette='Blues_d')
plt.ylim(0, 5)
plt.axhline(y=4.0, color='r', linestyle='--', label='Target Rating (4.0)')

plt.title('Average User Rating by Bank', fontsize=14, fontweight='bold')
plt.ylabel('Average Stars')
plt.xlabel('')
plt.legend()
plt.tight_layout()
plt.savefig('reports/figures/avg_rating.png')
print("✅ Saved chart: avg_rating.png")

# ------------------------------------------------------
# CHART 3: "Pain Points" Word Cloud (Negative Reviews)
# ------------------------------------------------------
# We join all text from reviews labeled "NEGATIVE"
negative_text = " ".join(review for review in df[df['sentiment_label'] == 'NEGATIVE']['review_text'].dropna())

if len(negative_text) > 0:
    # Generate Cloud
    wc = WordCloud(width=800, height=400, background_color='white', colormap='Reds').generate(negative_text)
    
    plt.figure(figsize=(10, 5))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.title('Common Pain Points (Keywords in Negative Reviews)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('reports/figures/pain_points_cloud.png')
    print("✅ Saved chart: pain_points_cloud.png")
else:
    print("ℹ️ Not enough negative data for Word Cloud.")

print("\n🎉 All charts generated! Check the 'reports/figures' folder.")