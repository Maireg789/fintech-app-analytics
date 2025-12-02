import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from wordcloud import WordCloud
import os
from dotenv import load_dotenv

# Load Config
load_dotenv()
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

if not DB_PASS:
    print("[ERROR] DB_PASS not found in .env file.")
    exit()

# Connect
engine = create_engine(f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

print("[INFO] Fetching data...")
query = """
SELECT r.review_text, r.rating, r.sentiment_label, b.bank_name
FROM reviews r
JOIN banks b ON r.bank_id = b.bank_id
"""
df = pd.read_sql(query, engine)

if not os.path.exists('reports/figures'):
    os.makedirs('reports/figures')

sns.set_theme(style="whitegrid")

# 1. Sentiment Distribution
plt.figure(figsize=(10, 6))
order = ['NEGATIVE', 'NEUTRAL', 'POSITIVE']
sns.countplot(data=df, x='bank_name', hue='sentiment_label', hue_order=order, palette='viridis')
plt.title('Sentiment Distribution per Bank', fontsize=14)
plt.tight_layout()
plt.savefig('reports/figures/sentiment_distribution.png')
print("[SUCCESS] Saved sentiment_distribution.png")

# 2. Avg Rating
plt.figure(figsize=(8, 5))
avg_rating = df.groupby('bank_name')['rating'].mean().reset_index()
sns.barplot(data=avg_rating, x='bank_name', y='rating', palette='Blues_d')
plt.axhline(y=4.0, color='r', linestyle='--', label='Target (4.0)')
plt.title('Average User Rating', fontsize=14)
plt.legend()
plt.tight_layout()
plt.savefig('reports/figures/avg_rating.png')
print("[SUCCESS] Saved avg_rating.png")

# 3. Pain Points
neg_text = " ".join(review for review in df[df['sentiment_label'] == 'NEGATIVE']['review_text'].dropna())
if len(neg_text) > 0:
    wc = WordCloud(width=800, height=400, background_color='white', colormap='Reds').generate(neg_text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.title('Common Pain Points', fontsize=14)
    plt.tight_layout()
    plt.savefig('reports/figures/pain_points_cloud.png')
    print("[SUCCESS] Saved pain_points_cloud.png")

print("\n[DONE] Charts generated successfully.")