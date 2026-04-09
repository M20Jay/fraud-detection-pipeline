# ================================================================
# Week 2 — Credit Card Fraud Detection Pipeline
# File: src/kafka_consumer.py
# Author: Martin James | github.com/M20Jay
# Purpose: Read transactions from Kafka topic
#          Call FastAPI /predict for each transaction
#          Print fraud scoring results in real time
# ================================================================

# ── 1. Imports ───────────────────────────────────────────────────
from kafka import KafkaConsumer
import json
import requests
import time

# ── 2. Kafka Consumer Setup ───────────────────────────────────────
consumer = KafkaConsumer(
    "fraud-transactions",
    bootstrap_servers = ['localhost:9092'],
    auto_offset_reset = 'earliest',
    value_deserializer = lambda v : json.loads(v.decode('utf-8'))
)

print("✅ Connected to Kafka — listening for transactions...")

# ── 3. FastAPI endpoint ───────────────────────────────────────────
FASTAPI_URL = "http://localhost:8000/predict"

# ── 4. Consume and Score Transactions ────────────────────────────
def consume_and_score():
    print("🔍 Scoring transactions in real time...\n")

    for message in consumer:
        transaction = message.value
        start_time = time.time()

        try:
            response = requests.post(FASTAPI_URL, json=transaction)

            if response.status_code == 200:
                result = response.json()
                elapsed = round((time.time() - start_time)*1000,2)
                risk    = result['risk_level']
                prob    = result['fraud_probability']
                amount  = transaction['amount']
                source  = result['source']
            
                flag = "⚠️  FRAUD ALERT" if result['fraud_predicted'] else "✅ Legitimate"
                print(f"{flag} | Amount: {amount:.2f} | "
                      f"Risk: {risk} | Probability: {prob} | "
                      f"Source: {source} | Time: {elapsed}ms")
            else:
                print(f"❌ FastAPI error: {response.status_code}")
        
        except Exception as e:
            print(f"❌ Error scoring transaction: {e}")

if __name__ == "__main__":
    consume_and_score()