# 📊 Customer Experience Analytics for Fintech Apps

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Status](https://img.shields.io/badge/Status-Interim_Complete-green)
![Libraries](https://img.shields.io/badge/Libraries-Pandas%20%7C%20Transformers%20%7C%20Scikit--Learn-orange)

## 📖 Project Overview
This project analyzes customer satisfaction for three major Ethiopian banking applications (**CBE**, **Bank of Abyssinia**, **Dashen**) by scraping and processing user reviews from the Google Play Store. 

The pipeline includes **web scraping**, **data cleaning**, **sentiment analysis (BERT)**, and **thematic clustering** to identify key satisfaction drivers and pain points.

## 📂 Project Structure
```text
fintech-app-analytics/
├── data/
│   ├── raw/                 # Scraped raw data
│   └── processed/           # Cleaned data with Sentiment & Themes
├── src/
│   ├── scraper.py           # Google Play Store scraper with retry logic
│   ├── preprocess.py        # Cleaning module (Deduplication, Date Norm)
│   ├── analysis.py          # NLP Pipeline (DistilBERT + TF-IDF)
│   └── database.py          # Database loader (PostgreSQL/SQLite)
├── reports/                 # Generated charts and PDF reports
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
