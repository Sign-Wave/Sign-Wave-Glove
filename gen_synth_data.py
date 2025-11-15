#!/usr/bin/env python3
"""
Generate synthetic data using SMOTE.

Usage:
    python generate_synthetic_data.py \
        --input data.csv \
        --output synthetic_data.csv
"""

import argparse
import pandas as pd
from imblearn.over_sampling import SMOTE


def load_data(path):
    """Load CSV dataset."""
    df = pd.read_csv(path)
    if "label" not in df.columns:
        raise ValueError("Input CSV must contain a 'label' column.")

    X = df.drop(columns=["label"])
    y = df["label"]
    return X, y


def apply_smote(X, y, k_neighbors=5):
    """Apply SMOTE oversampling."""
    sm = SMOTE(sampling_strategy="auto", k_neighbors=k_neighbors, random_state=42)
    X_res, y_res = sm.fit_resample(X, y)

    df_resampled = pd.DataFrame(X_res, columns=X.columns)
    df_resampled["label"] = y_res

    return df_resampled


def save_data(df, output_path):
    """Save synthetic dataset to CSV."""
    df.to_csv(output_path, index=False)
    print(f"Synthetic dataset saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate SMOTE synthetic dataset.")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--output", required=True, help="Path to save synthetic CSV")
    parser.add_argument("--neighbors", type=int, default=5,
                        help="Number of neighbors for SMOTE (default: 5)")

    args = parser.parse_args()

    print("Loading data...")
    X, y = load_data(args.input)

    print("Applying SMOTE...")
    df_synth = apply_smote(X, y, k_neighbors=args.neighbors)

    print("Saving synthetic dataset...")
    save_data(df_synth, args.output)

    print("Done!")


if __name__ == "__main__":
    main()
