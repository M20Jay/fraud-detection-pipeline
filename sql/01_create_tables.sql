-- ================================================================
-- Week 2 — Credit Card Fraud Detection Pipeline
-- File: sql/01_create_tables.sql
-- Author: Martin James | github.com/M20Jay
-- Purpose: Create all tables needed for the fraud pipeline
-- ================================================================


-- Table 1 — Raw fraud data loaded from creditcard.csv
-- This is the source of truth — never modified after loading
CREATE TABLE IF NOT EXISTS fraud_raw (
    id      SERIAL PRIMARY KEY,
    time    FLOAT,
    v1      FLOAT, v2  FLOAT, v3  FLOAT, v4  FLOAT,
    v5      FLOAT, v6  FLOAT, v7  FLOAT, v8  FLOAT,
    v9      FLOAT, v10 FLOAT, v11 FLOAT, v12 FLOAT,
    v13     FLOAT, v14 FLOAT, v15 FLOAT, v16 FLOAT,
    v17     FLOAT, v18 FLOAT, v19 FLOAT, v20 FLOAT,
    v21     FLOAT, v22 FLOAT, v23 FLOAT, v24 FLOAT,
    v25     FLOAT, v26 FLOAT, v27 FLOAT, v28 FLOAT,
    amount  FLOAT,
    class   INT
);


-- Table 2 — Every prediction the model makes in production
-- FastAPI writes here after scoring each transaction
CREATE TABLE IF NOT EXISTS fraud_predictions (
    id                  SERIAL PRIMARY KEY,
    transaction_id      VARCHAR(50),
    amount              FLOAT,
    fraud_probability   FLOAT,
    fraud_predicted     BOOLEAN,
    risk_level          VARCHAR(10),
    value_at_risk       FLOAT,
    model_version       VARCHAR(10),
    scored_at           TIMESTAMP DEFAULT NOW()
);


-- Table 3 — Model performance tracking
-- Written once after each model training run
CREATE TABLE IF NOT EXISTS fraud_metrics (
    id              SERIAL PRIMARY KEY,
    model_name      VARCHAR(50),
    roc_auc         FLOAT,
    pr_auc          FLOAT,
    precision_score FLOAT,
    recall_score    FLOAT,
    f1_score        FLOAT,
    threshold       FLOAT,
    trained_at      TIMESTAMP DEFAULT NOW()
);