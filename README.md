# Week 2 — Real-Time Credit Card Fraud Detection Pipeline

**Author:** Martin James | github.com/M20Jay  
**Status:** 🔨 In Progress — Day 2  
**Stack:** LightGBM · XGBoost · ADASYN · sklearn Pipeline · FastAPI · PostgreSQL · Redis · Prometheus · Grafana · Docker

---

## Business Problem

A bank loses money every time a fraudulent transaction goes undetected.  
This pipeline scores every transaction in real time and blocks fraud before it completes.  
Target: under 200ms per transaction.

---

## Architecture

    creditcard.csv
          ↓
    fraud_raw table (PostgreSQL)
          ↓
    Python reads from PostgreSQL → Feature Engineering → ADASYN → Train 4 Models
          ↓
    fraud_pipeline.pkl saved
          ↓
    FastAPI scores transactions → fraud_predictions table (PostgreSQL)
          ↓
    Prometheus scrapes API metrics every 15s
          ↓
    Grafana dashboard — business metrics + API performance

---

## Project Structure

    fraud-detection-pipeline/
    ├── data/                    # creditcard.csv (gitignored)
    ├── grafana/
    │   └── prometheus.yml       # Prometheus scrape config
    ├── notebooks/
    │   ├── 01_EDA_and_Feature_Engineering.ipynb
    │   └── 02_Preprocessing_and_Modelling.ipynb
    ├── sql/                     # Database table definitions
    ├── src/                     # Pipeline scripts
    ├── tests/                   # Unit tests
    ├── docker-compose.yml       # All services
    └── README.md

---

## Services

| Service    | Port | Purpose                                    |
|------------|------|--------------------------------------------|
| PostgreSQL | 5432 | Stores raw data and all predictions        |
| Redis      | 6379 | Caches recent predictions for speed        |
| Prometheus | 9090 | Scrapes FastAPI metrics every 15 seconds   |
| Grafana    | 3000 | Live dashboard — business and API metrics  |

---

## How to Run

    # Start all services
    docker compose up -d

    # Verify all containers are running
    docker compose ps

---

## Progress

| Day   | Task                                          | Status         |
|-------|-----------------------------------------------|----------------|
| Day 1 | EDA + Feature Engineering                     | ✅ Complete    |
| Day 2 | PostgreSQL setup + ADASYN + 4 Models + Pipeline | ✅ Complete  |
| Day 3 | FastAPI + Redis caching + Prometheus          | ⏳ Pending     |
| Day 4 | Kafka producer + consumer                     | ⏳ Pending     |
| Day 5 | Grafana dashboard                             | ⏳ Pending     |
| Day 6 | Business impact analysis                      | ⏳ Pending     |
| Day 7 | Deploy to Render                              | ⏳ Pending     |

---

## Dataset

Kaggle Credit Card Fraud Detection — 284,807 transactions — 0.17% fraud rate  
Features: 28 PCA components (V1-V28) + Amount + Time + Class

---

*Part of a 15-week MLOps programme building production ML systems from scratch.*