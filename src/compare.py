"""Compare candidate models by cross-validated PR-AUC.
Uses ONLY the training part. The sealed test set is not touched."""
import time

from sklearn.model_selection import StratifiedKFold, cross_validate

from modeling import SEED, build_pipeline, candidate_models
from train import load_data, split


def main():
    X_train, X_test, y_train, y_test = split(load_data())
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    print(f"No-skill PR-AUC (fraud rate): {y_train.mean():.5f}", flush=True)

    for name, model in candidate_models().items():
        t0 = time.time()
        res = cross_validate(
            build_pipeline(model), X_train, y_train,
            cv=cv, scoring="average_precision",
        )
        s = res["test_score"]
        folds = [round(float(x), 3) for x in s]
        print(f"{name:20s} PR-AUC {s.mean():.4f} +/- {s.std():.4f}  "
              f"folds={folds}  ({time.time() - t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
