# 💡 Strategic Insights & Recommendations
**Generated from:** `src/analysis.py` and `src/visualize.py` outputs.

This document codifies the link between our data findings and the proposed business actions.

## 1. Reliability Matrix (Infrastructure)
| Bank | Metric | Insight | Strategic Recommendation |
|------|--------|---------|--------------------------|
| **CBE** | **65%** Negative reviews contain "Network/OTP" | Users are satisfied with UI but blocked by backend failures. | **Stop Feature Dev:** Freeze new features for Q1. Redirect 100% of engineering resources to API Gateway scaling and SMS OTP redundancy. |
| **BoA** | **High** correlation between Updates & Negativity | Sentiment drops immediately after "New Version" releases. | **Implement Canary Releases:** Roll out updates to 5% of users first. If crash rate > 1%, auto-rollback. |

## 2. Feature & Lifestyle Matrix
| Bank | Metric | Insight | Strategic Recommendation |
|------|--------|---------|--------------------------|
| **Dashen** | Top Keywords: "Cinema", "DSTV" | Non-banking features are the primary driver of 5-star reviews. | **Expand Ecosystem:** Partner with ride-hailing apps (Ride/Feres) to integrate booking directly into Amole. |

## 3. Support Efficiency Matrix
| Context | Data Evidence | Action |
|---------|---------------|--------|
| **All Banks** | "Login Error" is the #2 overall complaint | Users struggle with password resets and account unlocking. | **AI Chatbot Integration:** Deploy an in-app bot specifically trained to handle "Forgot Password" flows, reducing call center volume by estimated 30%. |