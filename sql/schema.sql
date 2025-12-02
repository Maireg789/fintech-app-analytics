-- Database Schema for Fintech App Analytics
-- This file documents the structure required for Task 3

-- Table 1: Banks (Dimension Table)
CREATE TABLE IF NOT EXISTS banks (
    bank_id SERIAL PRIMARY KEY,
    bank_name VARCHAR(100) UNIQUE NOT NULL,
    app_name VARCHAR(100)
);

-- Table 2: Reviews (Fact Table)
CREATE TABLE IF NOT EXISTS reviews (
    review_id SERIAL PRIMARY KEY,
    bank_name VARCHAR(100), -- Foreign key logic handled in app or via join
    content TEXT,
    score INT,
    at TIMESTAMP,
    sentiment_label VARCHAR(50),
    sentiment_score FLOAT,
    theme VARCHAR(100),
    source VARCHAR(50) DEFAULT 'Google Play'
);

-- Index for faster querying by bank and date
CREATE INDEX idx_reviews_bank ON reviews(bank_name);
CREATE INDEX idx_reviews_date ON reviews(at);