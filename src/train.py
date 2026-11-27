"""Train the fraud model with honest evaluation.

Step 1: load the raw table and seal a test set.
The test set is NOT used for choosing models or thresholds.
"""
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split

from features import FEATURES, TARGET

SEED = 42


def load_data():
    load_dotenv()
    engine = create_engine(os.environ["DATABASE_URL"])
    df = pd.read_sql("SELECT * FROM fraud_raw", engine)
    df.columns = df.columns.str.lower()
    return df


def split(df):
    X = df[FEATURES]
    y = df[TARGET]
    return train_test_split(
        X, y, test_size=0.2, random_state=SEED, stratify=y
    )


if __name__ == "__main__":
    df = load_data()
    X_train, X_test, y_train, y_test = split(df)
    print(f"train: {len(X_train):,} rows, {int(y_train.sum())} fraud")
    print(f"test : {len(X_test):,} rows, {int(y_test.sum())} fraud")
