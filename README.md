# Week 2 — Real-Time Credit Card Fraud Detection Pipeline

**Author:** Martin James Ng'ang'a | github.com/M20Jay  
**Status:** ✅ Week 2 Complete — Grafana Dashboard Live  
**Stack:** Random Forest · XGBoost · LightGBM · ADASYN · sklearn Pipeline · FastAPI · PostgreSQL · Redis · Kafka · Prometheus · Grafana · Docker

---

## The Problem

A model that's 99.8% accurate can be completely useless — and worse, dangerous.

Fraud detection isn't just a classification problem. It's an adversarial one. Every model has a decision boundary — the exact point where "probably fine" becomes "flag this." An attacker doesn't need to beat the model; they only need to *map* that boundary, through repeated near-threshold probing, and walk around it. This is a real, documented attack class — **evasion attack** — and most fraud-detection writeups never mention it.

This project treats that seriously, from three angles:

### 1. Class imbalance

With 284,807 transactions and only 492 genuinely fraudulent (0.17%), the obvious metric — accuracy — actively lies. A model predicting "not fraud" for everything scores 99.83% while catching nothing.

Four models were trained and compared; the winner was selected by **PR-AUC**, the metric that can't be fooled by this level of imbalance.

### 2. The detection-response gap

A fraud score in isolation is not a decision. In production, this model is stage one of a five-stage pipeline:

`Detection → SIEM → Case Management → SOAR → Feedback`

![Five-stage detection to response pipeline](screenshots/day8_5stage_handoff.png)

The score is correlated against other signals in a **SIEM**, routed to a human analyst through **case management** with the reasoning attached, acted on through **SOAR** tooling (freeze, lock, escalate), and the analyst's final call flows back as a label that closes the loop into the next retrain.

This repo owns stage one, and is explicitly designed to hand off cleanly into the other four.

### 3. Model-level threats, not just data-level ones

| Threat | Mitigation |
|---|---|
| **Data poisoning** — manipulated labels gradually shifting what the model considers "normal" | Human-reviewed retraining — a challenger model must prove it beats the current one before it's ever promoted |
| **Model extraction** — querying the API enough times to reverse-engineer its logic | Returning `risk_level` and top contributing factors, not raw probabilities or full feature weights |

**Target:** under 200ms per transaction. **Achieved:** 22ms average response time, live, with every single prediction logged and explainable.

---

## Live API

🌐 [Interactive Docs](https://martin-mlops.com/fraud/docs)

---

## Architecture

    creditcard.csv (284,807 transactions)
          ↓
    fraud_raw table (PostgreSQL)
          ↓
    ADASYN balancing → 4 Models trained → Random Forest selected (best PR-AUC)
          ↓
    fraud_pipeline.pkl saved
          ↓
    FastAPI (:8002) scores transactions in real time
          ↓
    Redis (:6379) caches predictions (300s TTL)
          ↓
    Kafka producer → Kafka consumer (streaming pipeline)
          ↓
    fraud_predictions table (PostgreSQL) — 200 predictions stored
          ↓
    Prometheus (:9090) scrapes /metrics every 15s
          ↓
    Grafana (:3000) — 5-panel live monitoring dashboard

### In Practice

**FastAPI scoring transactions live:**

![FastAPI live scoring](screenshots/day4_fastapi.png)

**Kafka producer streaming from PostgreSQL:**

![Kafka producer](screenshots/day4_producer.png)

**Kafka consumer scoring in real time:**

![Kafka consumer](screenshots/day4_consumer.png)

**Grafana — 5-panel live monitoring:**

![Grafana dashboard](screenshots/day5_grafana.png)


---

## Project Structure

    fraud-detection-pipeline/
    ├── data/                        # creditcard.csv (gitignored)
    ├── screenshots/                 # Day screenshots
    │   ├── day4_fastapi.png
    │   ├── day4_producer.png
    │   ├── day4_consumer.png
    │   └── day5_grafana.png
    ├── notebooks/
    │   ├── 01_EDA_and_Feature_Engineering.ipynb
    │   └── 02_Preprocessing_and_Modelling.ipynb
    ├── sql/                         # Table definitions
    ├── src/
    │   ├── app.py                   # FastAPI + Redis + PostgreSQL
    │   ├── kafka_producer.py        # Streams transactions to Kafka
    │   ├── kafka_consumer.py        # Consumes and scores transactions
    │   └── load_raw_data.py         # Loads creditcard.csv → PostgreSQL
    ├── .python-version              # Python 3.11.9
    ├── docker-compose.yml           # All 6 services
    ├── prometheus.yml               # Prometheus scrape config
    └── README.md

---

## Services

| Service    | Port | Purpose                              |
|------------|------|--------------------------------------|
| PostgreSQL | 5433 | Stores raw data and all predictions  |
| Redis      | 6379 | Caches predictions (300s TTL)        |
| Kafka      | 9092 | Streaming transaction pipeline       |
| Zookeeper  | 2181 | Kafka coordination                   |
| Prometheus | 9090 | Scrapes FastAPI metrics every 15s    |
| Grafana    | 3000 | Live dashboard — 5 panels            |

---

## How to Run

    # 1. Start all Docker services
    docker compose up -d

    # 2. Kill local postgres if port conflict
    sudo pkill -u martinjames postgres

    # 3. Start FastAPI (Terminal 1)
    uvicorn src.app:app --reload --port 8000

    # 4. Start Kafka producer (Terminal 2)
    python src/kafka_producer.py

    # 5. Start Kafka consumer (Terminal 3)
    python src/kafka_consumer.py

---

## Progress

| Day   | Task                                            | Status       |
|-------|-------------------------------------------------|--------------|
| Day 1 | EDA + Feature Engineering                       | ✅ Complete  |
| Day 2 | ADASYN + 4 Models + Random Forest Pipeline saved     | ✅ Complete  |
| Day 3 | FastAPI + Redis caching + Prometheus            | ✅ Complete  |
| Day 4 | Kafka producer + consumer — real time streaming | ✅ Complete  |
| Day 5 | Grafana dashboard — 5 panels live               | ✅ Complete  |
| Day 6 | Business impact analysis                        | ✅ Complete  |
| Day 7 | Deploy to AWS EC2                                | ✅ Complete  |

---

## Day 6 — Business Impact Analysis

> SQL analysis run against 200 live predictions scored by the fraud detection pipeline.

| Metric | Value |
|--------|-------|
| Total Transactions Scored | 200 |
| Fraud Detected | 50 (25%) |
| Legitimate Transactions | 150 (75%) |
| Average Fraud Probability | 23.21% |
| Total Value at Risk (USD) | $4,504.47 |
| Average Fraudulent Amount | $85.11 |

**Key Finding:** The Random Forest model flagged 50 out of 200 transactions as fraudulent,
protecting **$4,504.47** in potential losses. Average fraudulent transaction value was
**$85.11** — consistent with real-world card-present fraud patterns.

---

## Day 5 — Grafana Dashboard

### Full Dashboard — 5 Panels Live

| Panel | Type | Metric |
|-------|------|--------|
| API Requests Per Minute | Time series | rate(http_requests_total[5m]) |
| Total Value at Risk (USD) | Gauge | SUM(value_at_risk) = $4,504 |
| Total Transactions Scored | Stat | COUNT = 200 |
| Risk Level Distribution | Bar gauge | HIGH=17 · MEDIUM=33 · LOW=150 |
| Recent Fraud Predictions | Table | fraud_probability · amount · risk_level |

---

## Day 4 — Kafka Real-Time Streaming

The full architecture is shown in **In Practice**, above.

---

## Dataset

Kaggle Credit Card Fraud Detection — 284,807 transactions — 0.17% fraud rate  
Features: 28 PCA components (V1-V28) + Amount + Time + Class  
Fraud cases: 492 | Legitimate: 284,315

---

*Part of a 15-week MLOps programme building production ML systems from scratch.*  
*github.com/M20Jay*