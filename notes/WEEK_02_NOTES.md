# Week 2 — Real-Time Credit Card Fraud Detection Pipeline
**Martin James Ng'ang'a · MLOps Engineer · Nairobi, Kenya 🇰🇪**
`github.com/M20Jay` · Week 2 of 15

---

## Overview

Production real-time fraud detection pipeline scoring 284,807 transactions at 22ms average response time. LightGBM model with Kafka streaming, Redis caching, Prometheus monitoring, and 5-panel Grafana dashboard.

**Target:** under 200ms per transaction. **Achieved:** 22ms average.

---

## Final Results

| Metric | Result |
|--------|--------|
| Dataset | 284,807 transactions · 0.17% fraud rate |
| Best Model | LightGBM · best PR-AUC |
| Response time | 22ms average |
| Fraud detected | 50 / 200 scored (25%) |
| Value protected | $4,504.47 |
| Average fraud amount | $85.11 |
| Live API | http://18.184.3.203:8003/docs |
| Grafana panels | 5 panels · requests, value at risk, transactions, risk levels, recent predictions |

---

## Business Impact

| Metric | Value |
|--------|-------|
| Total Transactions Scored | 200 |
| Fraud Detected | 50 (25%) |
| Legitimate Transactions | 150 (75%) |
| Average Fraud Probability | 23.21% |
| Total Value at Risk (USD) | $4,504.47 |
| Average Fraudulent Amount | $85.11 |

LightGBM flagged 50 out of 200 transactions as fraudulent, protecting **$4,504.47** in potential losses. Average fraudulent transaction value was **$85.11** — consistent with real-world card-present fraud patterns.

---

## 7-Day Build Plan

| Day | Task | Status |
|-----|------|--------|
| Day 1 | EDA + Feature Engineering | ✅ |
| Day 2 | ADASYN + 4 Models + LightGBM Pipeline saved | ✅ |
| Day 3 | FastAPI + Redis caching + Prometheus | ✅ |
| Day 4 | Kafka producer + consumer — real-time streaming | ✅ |
| Day 5 | Grafana dashboard — 5 panels live | ✅ |
| Day 6 | Business impact analysis | ✅ |
| Day 7 | README + Deploy to AWS EC2 | ✅ |

---

## Services

| Service | Port | Purpose |
|---------|------|---------|
| FastAPI | 8003 | Scores transactions in real time |
| PostgreSQL | 5433 | Stores raw data and all predictions |
| Redis | 6379 | Caches predictions (300s TTL) |
| Kafka | 9092 | Streaming transaction pipeline |
| Zookeeper | 2181 | Kafka coordination |
| Prometheus | 9090 | Scrapes FastAPI metrics every 15s |
| Grafana | 3000 | Live dashboard — 5 panels |

---

## Project Structure

```
fraud-detection-pipeline/
├── data/                       creditcard.csv (gitignored)
├── screenshots/                Day screenshots
├── notebooks/
│   ├── 01_EDA_and_Feature_Engineering.ipynb
│   └── 02_Preprocessing_and_Modelling.ipynb
├── sql/                        Table definitions
├── src/
│   ├── app.py                  FastAPI + Redis + PostgreSQL
│   ├── kafka_producer.py       Streams transactions to Kafka
│   ├── kafka_consumer.py       Consumes and scores transactions
│   └── load_raw_data.py        Loads creditcard.csv → PostgreSQL
├── prometheus.yml              Prometheus scrape config
├── docker-compose.yml          All 6 services
└── requirements.txt
```

---

## Pipeline Architecture

```
creditcard.csv (284,807 transactions)
    ↓
fraud_raw table (PostgreSQL)
    ↓
ADASYN balancing → 4 Models trained → LightGBM selected (best PR-AUC)
    ↓
fraud_pipeline.pkl saved
    ↓
FastAPI (:8003) scores transactions in real time
    ↓
Redis (:6379) caches predictions (300s TTL)
    ↓
Kafka producer → Kafka consumer (streaming pipeline)
    ↓
fraud_predictions table (PostgreSQL)
    ↓
Prometheus (:9090) scrapes /metrics every 15s
    ↓
Grafana (:3000) — 5-panel live monitoring dashboard
```

---

## Key Concepts

### Why LightGBM Over XGBoost for Fraud

```python
# 4 models evaluated — LightGBM wins on PR-AUC
# Fraud detection uses PR-AUC not ROC-AUC
# Why: 0.17% fraud rate — extreme class imbalance
# ROC-AUC is optimistic on imbalanced datasets
# PR-AUC measures precision-recall tradeoff — more honest

# LightGBM advantages for fraud:
# - Faster training on large datasets (284,807 rows)
# - Handles class imbalance with class_weight parameter
# - Leaf-wise tree growth vs XGBoost level-wise
# - Lower memory usage
```

### Why PR-AUC Not ROC-AUC for Fraud

```python
from sklearn.metrics import average_precision_score, roc_auc_score

# ROC-AUC on 0.17% fraud rate:
# True Negative Rate is enormous — artificially inflates AUC
# A model predicting "no fraud" for everyone gets ROC-AUC ~0.99

# PR-AUC is honest:
# Precision = of all flagged transactions, how many are actually fraud?
# Recall = of all actual fraud, how many did we catch?
# PR-AUC balances both — correct metric for extreme imbalance

pr_auc = average_precision_score(y_test, y_proba)
roc_auc = roc_auc_score(y_test, y_proba)
print(f"PR-AUC: {pr_auc:.4f}")   # honest
print(f"ROC-AUC: {roc_auc:.4f}") # optimistic
```

### ADASYN on Fraud Data

```python
from imblearn.over_sampling import ADASYN

# 492 fraud cases vs 284,315 legitimate — extreme imbalance
# ADASYN generates synthetic fraud samples near decision boundary
adasyn = ADASYN(random_state=42)
X_resampled, y_resampled = adasyn.fit_resample(X_train, y_train)

# Apply ONLY on training set — never on test set
# Test set must reflect real-world class distribution
```

### Redis Caching Pattern

```python
import redis
import json

redis_client = redis.Redis(host='redis', port=6379, db=0)

def get_cached_prediction(transaction_id: str):
    cached = redis_client.get(f"prediction:{transaction_id}")
    if cached:
        return json.loads(cached)
    return None

def cache_prediction(transaction_id: str, result: dict, ttl: int = 300):
    redis_client.setex(
        f"prediction:{transaction_id}",
        ttl,   # 300 seconds = 5 minutes
        json.dumps(result)
    )

# Cache flow:
# Request arrives → check Redis → if hit: return cached (fast)
#                              → if miss: run model → cache result → return
```

### Kafka Streaming Pattern

```python
# kafka_producer.py — streams transactions from PostgreSQL
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def stream_transaction(transaction: dict):
    producer.send('fraud-transactions', value=transaction)
    producer.flush()

# kafka_consumer.py — consumes and scores in real time
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'fraud-transactions',
    bootstrap_servers=['kafka:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

for message in consumer:
    transaction = message.value
    # Score transaction → save to PostgreSQL
    score_and_save(transaction)
```

### Prometheus Metrics Pattern

```python
from prometheus_client import Counter, Histogram, generate_latest
from fastapi import FastAPI
from fastapi.responses import Response

# Define metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency'
)

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")

# Prometheus scrapes /metrics every 15s (configured in prometheus.yml)
# Grafana reads from Prometheus → renders live panels
```

### Risk Level Classification

```python
def get_risk_level(fraud_probability: float) -> str:
    if fraud_probability >= 0.8:
        return "HIGH"
    elif fraud_probability >= 0.5:
        return "MEDIUM"
    else:
        return "LOW"

# Grafana Risk Level Distribution panel:
# HIGH=17 · MEDIUM=33 · LOW=150 (out of 200 scored)
```

---

## Grafana Dashboard — 5 Panels

| Panel | Type | Query |
|-------|------|-------|
| API Requests Per Minute | Time series | `rate(http_requests_total[5m])` |
| Total Value at Risk (USD) | Gauge | `SELECT SUM(amount) FROM predictions WHERE is_fraud=true` |
| Total Transactions Scored | Stat | `SELECT COUNT(*) FROM predictions` |
| Risk Level Distribution | Bar gauge | `SELECT risk_level, COUNT(*) FROM predictions GROUP BY risk_level` |
| Recent Fraud Predictions | Table | `SELECT fraud_probability, amount, risk_level FROM predictions ORDER BY created_at DESC LIMIT 20` |

---

## CLI Reference

### Start All Services

```bash
# Start everything
docker compose up -d

# Check all services running
docker compose ps

# Kill local postgres if port conflict on Mac
sudo pkill -u martinjames postgres
```

### Run Streaming Pipeline (3 terminals)

```bash
# Terminal 1 — FastAPI
uvicorn src.app:app --reload --port 8000

# Terminal 2 — Kafka producer
python src/kafka_producer.py

# Terminal 3 — Kafka consumer
python src/kafka_consumer.py
```

### API Testing

```bash
# Health check
curl -s http://localhost:8003/health | python3 -m json.tool

# Score a transaction
curl -s -X POST http://localhost:8003/predict \
  -H "Content-Type: application/json" \
  -d '{
    "V1": -1.359807, "V2": -0.072781, "V3": 2.536347,
    "V4": 1.378155, "V5": -0.338321, "V6": 0.462388,
    "V7": 0.239599, "V8": 0.098698, "V9": 0.363787,
    "V10": 0.090794, "V11": -0.551600, "V12": -0.617801,
    "V13": -0.991390, "V14": -0.311169, "V15": 1.468177,
    "V16": -0.470401, "V17": 0.207971, "V18": 0.025791,
    "V19": 0.403993, "V20": 0.251412, "V21": -0.018307,
    "V22": 0.277838, "V23": -0.110474, "V24": 0.066928,
    "V25": 0.128539, "V26": -0.189115, "V27": 0.133558,
    "V28": -0.021053, "Amount": 149.62, "Time": 0
  }' | python3 -m json.tool

# Prometheus metrics
curl -s http://localhost:9090/metrics | head -20
```

### Docker Commands

```bash
# View API logs
docker compose logs api --tail=20

# View Kafka logs
docker compose logs kafka --tail=20

# Restart specific service
docker compose restart api

# Stop everything
docker compose down

# Check port binding on server
sudo ss -tlnp | grep 8003
```

### Database Inspection

```bash
# Connect to PostgreSQL
docker compose exec postgres psql -U fraud -d fraud

# Inside psql:
\dt
SELECT COUNT(*) FROM predictions;
SELECT is_fraud, COUNT(*), AVG(fraud_probability), SUM(amount)
  FROM predictions GROUP BY is_fraud;
SELECT risk_level, COUNT(*) FROM predictions GROUP BY risk_level;
\q
```

### Model File Fix on Linux Server

```bash
# Mac path hardcoded in docker-compose — fix for Linux
sed -i 's/restart: unless-stopped/environment:\n      - MODEL_PATH=\/app\/src\/fraud_pipeline.pkl\n    restart: unless-stopped/' docker-compose-api.yml

# Verify fix
grep -A3 "MODEL_PATH" docker-compose-api.yml
```

---

## Debugging Reference

### Common Errors and Fixes

| Error | Fix |
|-------|-----|
| `Connection refused kafka:9092` | Wait 30s after `docker compose up` — Kafka takes time to start |
| `NoBrokersAvailable` | Check Kafka container running: `docker compose ps kafka` |
| `Address already in use port 5433` | PostgreSQL port conflict: `sudo pkill -u $(whoami) postgres` |
| `FileNotFoundError fraud_pipeline.pkl` | Set `MODEL_PATH` environment variable in docker-compose |
| `Redis connection refused` | Check Redis container: `docker compose ps redis` |
| `Prometheus target down` | Check FastAPI `/metrics` endpoint responding |

### Debugging Order

```
1. Check all containers running: docker compose ps
2. Check specific service logs: docker compose logs <service> --tail=50
3. Test API directly: curl http://localhost:8003/health
4. Test Redis: docker compose exec redis redis-cli ping → should return PONG
5. Test Kafka: docker compose exec kafka kafka-topics.sh --list --bootstrap-server localhost:9092
6. Test PostgreSQL: docker compose exec postgres psql -U fraud -d fraud -c "SELECT COUNT(*) FROM predictions;"
```

---

## AWS EC2 Deployment

```bash
# SSH to server
ssh -i ~/Documents/GitHub/mlops-key.pem ubuntu@18.184.3.203

# Start fraud detection API
cd ~/fraud-detection-pipeline
docker compose -f docker-compose-api.yml up -d

# Verify running
docker ps | grep fraud
curl -s http://localhost:8003/health

# Check logs
docker compose -f docker-compose-api.yml logs --tail=20
```

---

## Key Learnings from Week 2

- **PR-AUC not ROC-AUC for fraud** — ROC-AUC is misleading on extreme class imbalance (0.17% fraud rate)
- **Redis TTL matters** — 300 seconds balances cache freshness vs speed. Too long = stale predictions. Too short = no benefit
- **Kafka needs Zookeeper** — Zookeeper must start before Kafka — use `depends_on` in docker-compose
- **Model path hardcoded on Mac** — always use environment variables for file paths in Docker — never absolute paths
- **Prometheus pull model** — Prometheus pulls metrics from your app every 15s — your app exposes `/metrics`, Prometheus scrapes it
- **22ms response time** — Redis caching is the key — model inference alone is ~50ms, Redis cache hit is ~1ms

---

*Week 2 of 15 · Real-Time Fraud Detection Pipeline · Built in Nairobi, Kenya 🇰🇪*
*Live API: http://18.184.3.203:8003/docs · Repository: https://github.com/M20Jay/fraud-detection-pipeline*
