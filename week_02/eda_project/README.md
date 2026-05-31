# Document Reviews EDA Project

## Overview

This project performs exploratory data analysis on a document review dataset. The dataset contains document categories, word counts, review time, risk scores, and review status.

The goal is to understand document review patterns before building machine learning or AI systems on top of the data.

## Dataset Columns

- `document_id`: Unique identifier for each document
- `category`: Type of document, such as Legal, HR, Finance, Privacy, or Technical
- `word_count`: Number of words in the document
- `review_time_hours`: Time taken to review the document
- `risk_score`: Risk score assigned to the document
- `status`: Review outcome, such as approved, pending, or rejected

## Analysis Performed

The analysis script performs:

- dataset shape inspection
- first-row preview
- missing value checks
- category distribution analysis
- average word count calculation
- grouped category analysis for risk score and review time
- chart generation using Matplotlib and Seaborn

## Charts Created

The project saves the following charts in the `charts/` folder:

1. `1_category_count.png` - number of documents per category
2. `2_avg_risk.png` - average risk score by category
3. `3_word_count_vs_time.png` - relationship between word count and review time

## Key Findings

1. The dataset contains multiple document categories, which allows category-level comparison.
2. Average word count gives a quick sense of document size and review workload.
3. Grouped risk scores help identify which document categories may require more careful review.
4. Review time can be compared across categories to understand workload differences.
5. The scatter plot helps reveal whether longer documents usually require more review time.

## Why This Matters For AI Engineering

EDA is the first step before building reliable AI systems. For document AI, understanding word count, category distribution, risk levels, and review time helps design better document processing pipelines, review automation tools, and future RAG systems.

This project is a foundation for later AI engineering work such as:

- document classification
- risk prediction
- document search
- retrieval-augmented generation
- AI-assisted review workflows

## How To Run

From the repository root:

```powershell
python week_02\eda_project\eda_analysis.py