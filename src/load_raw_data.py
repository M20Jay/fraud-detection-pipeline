# ================================================================
# Week 2 — Credit Card Fraud Detection Pipeline
# File: src/load_raw_data.py
# Author: Martin James | github.com/M20Jay
# Purpose: Load creditcard.csv into PostgreSQL fraud_raw table
# Run once before training — this replaces pd.read_csv()
# ================================================================


# ── 1. Imports ───────────────────────────────────────────────────
import pandas as pd
from sqlalchemy import create_engine, text
import os
import time

# ── 2. Database Connection ───────────────────────────────────────
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg2://martin:martin123@127.0.0.1:5432/fraud_db"
)

engine =create_engine(DATABASE_URL)
print(f"Connecting to: {DATABASE_URL}")

# ── 3. Load CSV ──────────────────────────────────────────────────
CSV_PATH = os.path.expanduser(
    "~/Documents/GitHub/fraud-detection-pipeline/data/creditcard.csv"
)
print("Reading creditcard.csv...")

t0 = time.time()
df = pd.read_csv(CSV_PATH)
df.columns = df.columns.str.lower()

print(f"Shape        : {df.shape}")
print(f"Fraud cases  : {(df['class']==1).sum():,} ({df['class'].mean()*100:.3f}%)")
print(f"Legit cases  : {(df['class']==0).sum():,}")
print(f"Read time    : {time.time() - t0:.1f}s")

# ── 4. Load into PostgreSQL ──────────────────────────────────────
print("\nLoading into PostgreSQL fraud_raw table...")
t1 = time.time()

df.to_sql(
    name      = "fraud_raw",
    con       = engine,
    if_exists = "replace",
    index     = False,
    chunksize = 1000
)

elapsed = time.time() - t1
print(f"✅ Done — {len(df):,} rows loaded in {elapsed:.1f}s")
print(f"Table: fraud_raw")
print(f"Database: fraud_db")

# ── 5. Verify Loading ────────────────────────────────────────────
print("\nVerifying data in PostgreSQL...")

with engine.connect() as conn:
    total = conn.execute(text("SELECT COUNT(*) FROM fraud_raw")).scalar()
    fraud = conn.execute(text("SELECT COUNT(*) FROM fraud_raw WHERE class = 1")).scalar()
    legit = conn.execute(text("SELECT COUNT(*) FROM fraud_raw WHERE class = 0")).scalar()

print(f"Total rows   : {total:,}")
print(f"Fraud rows   : {fraud:,}")
print(f"Legit rows   : {legit:,}")
print(f"\n✅ fraud_raw table ready for training pipeline")
