# ================================================================
# Week 2 — Credit Card Fraud Detection Pipeline
# File: src/app.py
# Author: Martin James | github.com/M20Jay
# Purpose: FastAPI application — real time fraud scoring
#          Loads fraud_pipeline.pkl and scores transactions
#          Redis caching — Prometheus metrics — PostgreSQL logging
# ================================================================
# ── 1. Imports ───────────────────────────────────────────────────
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
import redis
import json
import hashlib
import os
import time
from sqlalchemy import create_engine,text
from prometheus_fastapi_instrumentator import Instrumentator

# ── 2. App Setup ─────────────────────────────────────────────────
app = FastAPI(
    title = "fraud Detection API",
    description = "Real-time credit card fraud scoring pipeline",
    version ="1.0.0"
)
# ── 3. Load Pipeline ─────────────────────────────────────────────
MODEL_PATH = os.path.expanduser("~/Documents/GitHub/fraud-detection-pipeline/src/fraud_pipeline.pkl")
pipeline = joblib.load(MODEL_PATH)
print(f"✅ Pipeline loaded — {MODEL_PATH}")

# ── 4. Database Connection ────────────────────────────────────────
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg2://martin:martin123@127.0.0.1:5432/fraud_db"
)
engine = create_engine(DATABASE_URL)
print(f"✅ Database connected")

# ── 5. Redis Connection ───────────────────────────────────────────
redis_client = redis.Redis(
    host = "localhost",
    port = 6379,
    db = 0,
    decode_responses = True
)

print(f"✅ Redis connected")

# ── 6. Prometheus ─────────────────────────────────────────────────
Instrumentator().instrument(app).expose(app)

# ── 7. Transaction Input Model ────────────────────────────────────
class Transaction(BaseModel):
    time:   float
    v1:     float
    v2:     float
    v3:     float
    v4:     float
    v5:     float
    v6:     float
    v7:     float
    v8:     float
    v9:     float
    v10:    float
    v11:    float
    v12:    float
    v13:    float
    v14:    float
    v15:    float
    v16:    float
    v17:    float
    v18:    float
    v19:    float
    v20:    float
    v21:    float
    v22:    float
    v23:    float
    v24:    float
    v25:    float
    v26:    float
    v27:    float
    v28:    float
    amount: float

# ── 8. Health Endpoint ────────────────────────────────────────────
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model"   : "Random Forest",
        "version" : "1.0.0"
    }

# ── 9. Predict Endpoint ───────────────────────────────────────────
@app.post("/predict")
def predict(transaction: Transaction):
    start_time = time.time()

    # ── Redis Cache Check ─────────────────────────────────────
    transaction_dict = transaction.model_dump()
    cache_key = hashlib.md5(
        json.dumps(transaction_dict, sort_keys = True).encode()).hexdigest()
    
    cached = redis_client.get(cache_key)
    if cached:
        result = json.loads(cached)
        result["source"] = "cache"
        return result

    # ── Model Scoring ─────────────────────────────────────────
    features = np.array([[
        transaction_dict["time"],
        transaction_dict["v1"],  transaction_dict["v2"],
        transaction_dict["v3"],  transaction_dict["v4"],
        transaction_dict["v5"],  transaction_dict["v6"],
        transaction_dict["v7"],  transaction_dict["v8"],
        transaction_dict["v9"],  transaction_dict["v10"],
        transaction_dict["v11"], transaction_dict["v12"],
        transaction_dict["v13"], transaction_dict["v14"],
        transaction_dict["v15"], transaction_dict["v16"],
        transaction_dict["v17"], transaction_dict["v18"],
        transaction_dict["v19"], transaction_dict["v20"],
        transaction_dict["v21"], transaction_dict["v22"],
        transaction_dict["v23"], transaction_dict["v24"],
        transaction_dict["v25"], transaction_dict["v26"],
        transaction_dict["v27"], transaction_dict["v28"],
        transaction_dict["amount"]
    ]])

    fraud_probability = pipeline.predict_proba(features)[0][1]
    fraud_predicted = bool(fraud_probability > 0.5)
    risk_level = "HIGH" if fraud_probability >= 0.7 else \
        "MEDIUM" if fraud_probability >= 0.3 else "LOW"
    response_time = round((time.time() - start_time) * 1000, 2)

    result = {
        "fraud_probability" : round(float(fraud_probability), 4),
        "fraud_predicted"   : fraud_predicted,
        "risk_level"        : risk_level,
        "response_time_ms"  : response_time,
        "model_version"     : "1.0.0",
        "source"            : "model"
    }
    # ── Cache Result in Redis ─────────────────────────────────
    redis_client.setex(cache_key, 300, json.dumps(result))

    # ── Save to PostgreSQL ────────────────────────────────────
    save_prediction(transaction_dict, result)

    return result

# ── 10. Save Prediction to PostgreSQL ────────────────────────────
def save_prediction(transaction_dict: dict, result: dict):
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO fraud_predictions (
                    amount,
                    fraud_probability,
                    fraud_predicted,
                    risk_level,
                    value_at_risk,
                    model_version
                ) VALUES (
                    :amount,
                    :fraud_probability,
                    :fraud_predicted,
                    :risk_level,
                    :value_at_risk,
                    :model_version
                )
            """), {
                "amount"            : transaction_dict["amount"],
                "fraud_probability" : result["fraud_probability"],
                "fraud_predicted"   : result["fraud_predicted"],
                "risk_level"        : result["risk_level"],
                "value_at_risk"     : transaction_dict["amount"] * result["fraud_probability"],
                "model_version"     : result["model_version"]
            })
            conn.commit()
    except Exception as e:
        print(f"❌ Database save failed: {e}")