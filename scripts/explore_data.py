"""
scripts/explore_data.py — Quick EDA helper
==========================================
Prints basic statistics about the raw PhysioNet dataset.
Run this interactively to understand the data before training.

Usage
-----
    python scripts/explore_data.py
"""

from pathlib import Path
import pandas as pd

RAW_DATA_PATH = Path(__file__).parent.parent / "Dataset.csv"

if not RAW_DATA_PATH.exists():
    raise FileNotFoundError(
        f"Raw dataset not found at {RAW_DATA_PATH}.\n"
        "Download it from https://physionet.org/ and place it in the project root."
    )

df = pd.read_csv(RAW_DATA_PATH)

print("Shape (rows, columns):", df.shape)
print("\nColumn names:")
print(df.columns.tolist())
print("\nFirst 5 rows:")
print(df.head())
print("\nBasic statistics:")
print(df.describe())
print("\nMissing values per column:")
print(df.isnull().sum())
print("\nSepsisLabel distribution:")
print(df["SepsisLabel"].value_counts())
