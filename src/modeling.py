"""Model pipelines. Scaling and ADASYN happen INSIDE the pipeline,
so during cross-validation they only ever see the training part
of each fold (no leakage), and predict() never applies ADASYN."""
from imblearn.over_sampling import ADASYN
from imblearn.pipeline import Pipeline
from lightgbm import LGBMClassifier
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from features import SCALE_COLS

SEED = 42


def build_pipeline(model):
    prep = ColumnTransformer(
        [("scale", StandardScaler(), SCALE_COLS)],
        remainder="passthrough",
    )
    return Pipeline([
        ("prep", prep),
        ("adasyn", ADASYN(random_state=SEED, n_neighbors=5)),
        ("model", model),
    ])


def candidate_models():
    return {
        "LogisticRegression": LogisticRegression(max_iter=1000),
        "RandomForest": RandomForestClassifier(
            n_estimators=200, n_jobs=-1, random_state=SEED),
        "LightGBM": LGBMClassifier(random_state=SEED, verbose=-1),
    }
