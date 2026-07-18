# 📊 Enterprise Attrition & Retention Analytics

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://enterprise-attrition-retention-analytics.streamlit.app/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=flat&logo=sqlite&logoColor=white)](https://www.sqlite.org/index.html)

**[🔴 Live Dashboard: Click Here to View the Interactive App](https://enterprise-attrition-retention-analytics.streamlit.app/)**

---

## 🎯 Project Objective
This project is an end-to-end data analytics pipeline designed to identify the primary drivers of customer attrition. It transitions from rigorous backend data engineering into a highly interactive, Power BI-style diagnostic web dashboard. The objective is to move beyond static reporting and deliver actionable, dynamic insights for retention teams.

## ⚙️ Technical Architecture & Data Pipeline
This project demonstrates a complete analytics workflow, strictly avoiding basic spreadsheet analysis in favor of robust programmatic execution:

*   **Data Engineering (SQLite):** Raw data ingestion simulating a production database environment.
*   **Advanced Query Logic:** Data extraction and feature engineering were executed using heavily optimized, multi-level **nested subqueries**. Standard table joins were strictly avoided to demonstrate a deep, rigorous understanding of database management systems, aggregation, and query execution order.
*   **Data Visualization (Plotly):** Interactive proportional stacked bars, variance boxplots, and financial density matrices.
*   **Deployment (Streamlit):** A custom-styled, interactive web application featuring an asymmetric enterprise grid layout and dynamic CSS framing.

## 🧠 Key Business Insights
The automated diagnostic engine dynamically calculates insights based on user filters. Baseline findings include:

1.  **Delinquency Impact:** Churned accounts consistently delay payments significantly longer than retained accounts, serving as the primary leading indicator of attrition.
2.  **Lifecycle Risk Zone:** The highest volume of churn occurs at a specific early-tenure month, indicating an onboarding and early-lifecycle engagement gap rather than a long-term product defect.
3.  **Financial Matrix:** Age and Total Spend clusters reveal that high-value customers exhibit distinct retention patterns compared to lower-tier brackets.

## 🚀 How to Run Locally

To run this pipeline on your local machine:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YourUsername/customer-attrition-analytics.git](https://github.com/YourUsername/customer-attrition-analytics.git)
   cd customer-attrition-analytics
