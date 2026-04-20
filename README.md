# Content Intelligence System

## Overview

This project explores how to evaluate text-based content across three dimensions:

* **Category** – what the content is about
* **Suitability** – whether it is appropriate for a younger / brand-sensitive audience
* **Performance** – how well the content is likely to engage users

The goal is to simulate how a brand or marketing partner might assess content before deciding whether to promote or associate with it.

---

## Dataset

The dataset consists of Reddit posts, where each row represents a single post with associated text, metadata, and engagement signals.

Initial observations:

* The primary text feature is the **post title**
* The `body` field is not populated and is not used
* Engagement is approximated using:

  * `score` (upvotes)
  * `num_comments`
  * `upvote_ratio`
* Additional metadata includes subreddit, timestamps, and content flags (e.g. NSFW)

Reddit is used as a proxy for real-world content, where tone and suitability vary widely.

---

## Approach

This project will follow a simple, end-to-end pipeline:

1. **Exploratory Data Analysis (EDA)**

   * Understand structure, distributions, and data quality
   * Identify usable signals and limitations

2. **Feature Engineering**

   * Text processing on titles
   * Creation of proxy labels for:

     * category
     * suitability
     * performance

3. **Modelling**

   * Classification model for content category
   * Heuristic or model-based approach for suitability
   * Predictive model for performance (engagement proxy)

4. **Output**

   * A simple interface (API or app) to evaluate new content

---

## Project Structure

```text
├── data/           # raw and processed data (not committed)
├── notebooks/      # EDA and experimentation
├── .gitignore
└── README.md
```

---

## Setup

Create and activate the project environment:

```bash
pyenv virtualenv 3.12.9 content-intel-env
pyenv local content-intel-env
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Launch the project:

```bash
jupyter lab
# or
code .
```

---

## Current Status

* Dataset loaded and initial structure explored
* EDA in progress
* Label definition and modelling to follow

---

## Notes

This is a portfolio project designed to simulate real-world product use cases.
Data and labels are approximations rather than production-grade ground truth.
