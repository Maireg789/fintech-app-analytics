# Fintech Customer Sentiment Analysis

## 📌 Project Overview
This project analyzes customer sentiment for three Ethiopian banking apps: **CBE, BoA, and Dashen (Amole)**. We scraped Google Play Store reviews, stored them in a PostgreSQL database, and analyzed them to identify key drivers and pain points.

## 🛠️ Tech Stack
- **Data Collection:** `google-play-scraper`
- **Processing:** `pandas`, `numpy`
- **NLP:** `HuggingFace Transformers` (DistilBERT)
- **Database:** PostgreSQL (`sqlalchemy`, `psycopg2`)
- **Visualization:** `matplotlib`, `seaborn`, `wordcloud`

## 📂 Project Structure
├── data/ # Raw and processed CSVs
├── src/
│ ├── scraper.py # Google Play Store Scraper
│ ├── database.py # ETL Pipeline (CSV -> Postgres)
│ ├── visualize.py # Generates charts for the report
├── reports/
│ ├── figures/ # Generated PNG charts
│ └── Final_Report.pdf
├── requirements.txt
└── README.md
## 🗄️ Database Architecture & Schema

The project uses a normalized Relational Database (PostgreSQL) to ensure data integrity and reduce redundancy.

### Entity Relationship Diagram (ERD)
```mermaid
erDiagram
    BANKS ||--o{ REVIEWS : "receives"
    BANKS {
        int bank_id PK "Primary Key"
        varchar bank_name "Official Name"
        varchar app_name "App Store Name"
    }
    REVIEWS {
        int review_id PK "Primary Key"
        int bank_id FK "Foreign Key -> banks.bank_id"
        text review_text "Raw User Feedback"
        int rating "1-5 Star Rating"
        date review_date "Date Posted"
        varchar sentiment_label "POS/NEU/NEG"
        float sentiment_score "Confidence Score"
    }