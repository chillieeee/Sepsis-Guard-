"""
train_model.py — SepsisGuard Model Training Script
====================================================
Trains a Random Forest classifier on the per-patient summary dataset and
saves the resulting model to disk as ``sepsis_model.pkl``.

Prerequisites
-------------
* patient_summary.csv must exist (run prepare_data.py first).
* pip install -r requirements.txt

Usage
-----
    python train_model.py

Output
------
    sepsis_model.pkl    — serialised RandomForestClassifier (joblib format)
"""

import logging
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DATA_PATH = Path("patient_summary.csv")
MODEL_PATH = Path("sepsis_model.pkl")
RANDOM_STATE = 42
TEST_SIZE = 0.20
N_ESTIMATORS = 200

FEATURES = [
    "HR", "O2Sat", "Temp", "SBP", "MAP", "Resp",
    "BUN", "Creatinine", "Glucose", "WBC", "Age", "Gender",
]
TARGET = "SepsisLabel"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def load_data(path: Path) -> pd.DataFrame:
    """Load and validate the patient-summary CSV."""
    if not path.exists():
        logger.error(
            "Data file '%s' not found.  Run prepare_data.py first.", path
        )
        sys.exit(1)

    df = pd.read_csv(path, index_col=0)
    logger.info("Loaded %d patients from '%s'.", len(df), path)

    missing_cols = [c for c in FEATURES + [TARGET] if c not in df.columns]
    if missing_cols:
        logger.error("Missing expected columns: %s", missing_cols)
        sys.exit(1)

    return df


def prepare_features(df: pd.DataFrame):
    """Extract feature matrix X and target vector y; impute with column means."""
    X = df[FEATURES].copy()
    y = df[TARGET]

    n_missing = X.isnull().sum().sum()
    if n_missing:
        logger.info(
            "Imputing %d missing values with column means.", n_missing
        )
        X = X.fillna(X.mean())

    logger.info(
        "Class distribution — No Sepsis: %d | Sepsis: %d",
        (y == 0).sum(),
        (y == 1).sum(),
    )
    return X, y


def train(X_train, y_train) -> RandomForestClassifier:
    """Fit a balanced Random Forest classifier."""
    clf = RandomForestClassifier(
        n_estimators=N_ESTIMATORS,
        random_state=RANDOM_STATE,
        class_weight="balanced",
        n_jobs=-1,
    )
    clf.fit(X_train, y_train)
    return clf


def evaluate(clf, X_test, y_test) -> None:
    """Print a classification report and AUC-ROC score."""
    y_pred = clf.predict(X_test)
    y_prob = clf.predict_proba(X_test)[:, 1]

    print("\n--- Classification Report ---")
    print(classification_report(y_test, y_pred, target_names=["No Sepsis", "Sepsis"]))

    auc = roc_auc_score(y_test, y_prob)
    logger.info("AUC-ROC score: %.4f", auc)


def main() -> None:
    logger.info("=== SepsisGuard Model Training ===")

    df = load_data(DATA_PATH)
    X, y = prepare_features(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    logger.info(
        "Train / test split: %d / %d patients.", len(X_train), len(X_test)
    )

    logger.info("Training Random Forest (%d estimators)...", N_ESTIMATORS)
    clf = train(X_train, y_train)

    evaluate(clf, X_test, y_test)

    joblib.dump(clf, MODEL_PATH)
    logger.info("Model saved to '%s'.", MODEL_PATH)
    print(f"\nModel saved to {MODEL_PATH}")


if __name__ == "__main__":
    main()
