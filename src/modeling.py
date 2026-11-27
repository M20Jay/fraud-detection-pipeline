"""Model pipelines. Scaling happens INSIDE the pipeline, so during
cross-validation it only sees the training part of each fold, and the
saved pipeline applies the same scaling when serving.

Class imbalance is handled with class weights, not resampling: ADASYN was
tested against class weights on this data (stratified 5-fold CV, PR-AUC)
and gave no reliable gain, so it was dropped."""
from lightgbm import LGBMClassifier  # kept out of candidates, see README
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from features import SCALE_COLS

SEED = 42


def imbalance_ratio(y):
    """Normal rows per fraud row, used as scale_pos_weight."""
    return (y == 0).sum() / (y == 1).sum()


def build_pipeline(model):
    prep = ColumnTransformer(
        [("scale", StandardScaler(), SCALE_COLS)],
        remainder="passthrough",
    )
    return Pipeline([
        ("prep", prep),
        ("model", model),
    ])


def candidate_models(ratio):
    return {
        "LogisticRegression (class_weight)": LogisticRegression(
            max_iter=1000, class_weight="balanced"),
        "RandomForest (class_weight)": RandomForestClassifier(
            n_estimators=100, n_jobs=-1, random_state=SEED,
            class_weight="balanced"),
        "XGBoost (scale_pos_weight)": XGBClassifier(
            eval_metric="logloss", n_jobs=-1, random_state=SEED,
            scale_pos_weight=ratio),
    }