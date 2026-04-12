# ================================================================
# Week 2 — Credit Card Fraud Detection Pipeline
# File: src/kafka_producer.py
# Author: Martin James | github.com/M20Jay
# Purpose: Read transactions from PostgreSQL fraud_raw table
#          and send each one to Kafka topic "fraud-transactions"
#          Simulates real-time transaction stream
# ================================================================
# ── 1. Imports ───────────────────────────────────────────────────
from kafka import KafkaProducer
import json
import time
import os
from sqlalchemy import create_engine, text

# ── 2. Database Connection ────────────────────────────────────────
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg2://martin:martin123@127.0.0.1:5433/fraud_db"
)

engine =create_engine(DATABASE_URL)
print("✅ Connected to PostgreSQL")

# ── 3. Kafka Producer Setup ───────────────────────────────────────
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer =lambda v: json.dumps(v).encode('utf-8')
    )
print("✅ Connected to Kafka")

# ── 4. Read from PostgreSQL and Send to Kafka ─────────────────────
def send_transactions():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM fraud_raw LIMIT 100"))
        rows = result.fetchall()
    print(f"📦 Sending {len(rows)} transactions to Kafka...")
    
    for i, row in enumerate(rows):
        transaction = dict(row._mapping)
        producer.send('fraud-transactions', value =transaction)
        producer.flush()
        print(f"✅ Sent transaction {i+1} — amount: {transaction['amount']:.2f}")
        time.sleep(1)
    
    producer.close()
    print(f"\n✅ All {len(rows)} transactions sent to Kafka")
if __name__ == "__main__":
    send_transactions()