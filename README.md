# 📊 Customer Experience Analytics for Fintech Apps

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Status](https://img.shields.io/badge/Status-Interim_Complete-green)
![Libraries](https://img.shields.io/badge/Libraries-Pandas%20%7C%20Transformers%20%7C%20Scikit--Learn-orange)

## 📖 Project Overview
This project provides a comprehensive data engineering pipeline to analyze customer satisfaction for Ethiopia's leading banking applications: **Commercial Bank of Ethiopia (CBE)**, **Bank of Abyssinia (BOA)**, and **Dashen Bank**.

By scraping Google Play Store reviews and applying **Natural Language Processing (NLP)**, this tool identifies key satisfaction drivers and technical pain points (e.g., Authentication failures, App Stability) to guide product improvements.

## 🔑 Key Features
*   **Robust Scraping:** Automated data collection with retry logic and rate limiting (`src/scraper.py`).
*   **Advanced Preprocessing:** Strict data quality gates including deduplication, date normalization, and missing value enforcement (`src/preprocess.py`).
*   **NLP Pipeline:** Hybrid analysis using **DistilBERT** for sentiment scoring and **TF-IDF** for keyword extraction (`src/analysis.py`).
*   **Evidence Generation:** Automated creation of summary tables and charts for stakeholder reporting (`src/generate_evidence.py`).
*   **Data Persistence:** Scalable storage using SQL (PostgreSQL/SQLite).

## 📂 Repository Structure
```text
fintech-app-analytics/
├── data/
│   ├── raw/                 # Raw scraped CSVs
│   └── processed/           # Cleaned data enriched with Sentiment & Themes
├── reports/
│   └── figures/             # Generated charts (Sentiment distribution, Word clouds)
├── src/
│   ├── scraper.py           # Data collection module
│   ├── preprocess.py        # Data cleaning & deduplication logic
│   ├── analysis.py          # Sentiment & Thematic analysis pipeline
│   ├── generate_evidence.py # Generates tables/charts for reports
│   ├── database.py          # SQL loader (PostgreSQL/SQLite)
│   └── utils.py             # Centralized logging configuration
├── requirements.txt         # Project dependencies
└── README.md                # Documentation
