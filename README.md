# Content Promotion Planner

## Overview

This project explores how machine learning predictions can be used to support real-world content promotion decisions.

To produce a practical promotion plan, it combines:

- **Engagement prediction** (how likely content is to perform well)
- **Safety assessment** (how suitable content is for a brand)
- **Simple business rules** (budget and risk thresholds)

👉 In simple terms:
*It helps decide which content to promote so that it performs well without taking on unnecessary risk.*

🚀 [Live demo]()

---

## Problem

Marketing teams often need to decide:

> *Which content should we promote, given limited budget and brand safety constraints?*

This project simulates that decision process by turning model outputs into an actionable plan.

---

## Approach

The project is structured as a lightweight end-to-end pipeline:

### 1. Content scoring

Each post is scored on:
- **Engagement probability** - likelihood of strong performance
- **Safety risk** - likelihood of being unsuitable for promotion

These are derived from Reddit data as a proxy for real-world content.

---

### 2. Decision layer

A simple planner applies business rules:

1. Filter out content above a safety threshold
2. Rank remaining content by engagement
3. Promote the top posts within a fixed budget

This produces:
- A recommended promotion set
- Expected performance and value
- Visibility into trade-offs (budget vs safety vs reach)

---

### 3. Interactive prototype

A Streamlit app allows users to explore:

- How many posts to promote
- Expected return (ROI)
- How changing safety tolerance or budget affects outcomes

The app focuses on the **decision layer**, not model training.

---

## Dataset

The dataset consists of Reddit posts, used as a proxy for real-world content:

- **Text**: post titles (primary feature)
- **Engagement signals**:
  - `score` (upvotes)
  - `num_comments`
  - `upvote_ratio`
- **Metadata**:
  - subreddit
  - timestamps
  - NSFW flags

Reddit provides a wide range of tone, quality, and suitability, making it useful for simulating content evaluation problems.

---

## Project Structure

```text
├── data/                # raw and processed data (not committed)
├── notebooks/           # modelling and decision logic
├── app.py               # Streamlit prototype
├── requirements.txt
└── README.md
