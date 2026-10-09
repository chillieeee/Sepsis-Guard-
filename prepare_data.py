"""
prepare_data.py — SepsisGuard Data Preparation Script
======================================================
Reads the raw PhysioNet Sepsis ICU dataset (Dataset.csv) and produces a
single-row-per-patient summary file (patient_summary.csv) suitable for
model training.

Strategy
--------
* Numeric columns are averaged across all timesteps for each patient.
* SepsisLabel is set to 1 if the patient was ever labelled septic (max over time).

Prerequisites
-------------
* Dataset.csv must be present in the project root (not tracked in Git due to size).
* pip install -r requirements.txt

Usage
-----
    python prepare_data.py

Output
------
    patient_summary.csv   — one row per patient, ready for train_model.py
"""

import logging
import sys
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
RAW_DATA_PATH = Path("Dataset.csv")
OUTPUT_PATH = Path("patient_summary.csv")
PATIENT_ID_COL = "Patient_ID"
TARGET_COL = "SepsisLabel"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def load_raw(path: Path) -> pd.DataFrame:
    """Load raw time-series ICU dataset."""
    if not path.exists():
        logger.error(
            "Raw dataset '%s' not found in the project root.\n"
            "Download it from https://physionet.org/ and place it here.",
            path,
        )
        sys.exit(1)

    logger.info("Loading '%s'...", path)
    df = pd.read_csv(path)
    logger.info("  Shape: %s", df.shape)
    logger.info("  Columns: %s", df.columns.tolist())
    return df


def aggregate(df: pd.DataFrame) -> pd.DataFrame:
    """Collapse time-series rows into one summary row per patient."""
    if PATIENT_ID_COL not in df.columns:
        logger.error("Column '%s' not found in the dataset.", PATIENT_ID_COL)
        sys.exit(1)

    # Mean across all timesteps for numeric columns
    patient_data = df.groupby(PATIENT_ID_COL).mean(numeric_only=True)

    # Override SepsisLabel: positive if *ever* septic
    patient_data[TARGET_COL] = df.groupby(PATIENT_ID_COL)[TARGET_COL].max()

    return patient_data


def report(df: pd.DataFrame) -> None:
    """Print a summary of the aggregated dataset."""
    print(f"\nPatients (rows): {len(df)}")
    print(f"Features  (cols): {df.shape[1]}")
    print("\nSepsis distribution:")
    print(df[TARGET_COL].value_counts().rename({0: "No Sepsis", 1: "Sepsis"}).to_string())
    print("\nMissing values per feature:")
    missing = df.isnull().sum()
    print(missing[missing > 0].to_string() or "  None")


def main() -> None:
    logger.info("=== SepsisGuard Data Preparation ===")

    df_raw = load_raw(RAW_DATA_PATH)
    df_patients = aggregate(df_raw)
    report(df_patients)

    df_patients.to_csv(OUTPUT_PATH)
    logger.info("Saved patient summary to '%s'.", OUTPUT_PATH)
    print(f"\nSaved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
