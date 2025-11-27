## 🛠 Update: Data Quality Enhancements
**Date:** 27 Nov 2025

Based on feedback, the following improvements were implemented in the `src/preprocess.py` pipeline:
- **Strict Deduplication:** Automatic removal of duplicate reviews based on content and bank name.
- **Date Normalization:** Enforced `datetime` conversion to ensure time-series accuracy.
- **Missingness Checks:** Strict removal of rows missing critical analysis fields (`content`, `score`).