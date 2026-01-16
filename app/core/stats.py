# app/core/stats.py

import pandas as pd

def compute_amount_stats(df: pd.DataFrame) -> dict:
    """
    Compute mean and standard deviation of the 'amount' column.
    Returns a dictionary with 'mean' and 'std'.
    """
    if 'amount' not in df.columns:
        return {"mean": 0.0, "std": 0.0}

    mean_amount = df['amount'].mean()
    std_amount = df['amount'].std()

    return {
        "mean": float(mean_amount) if pd.notna(mean_amount) else 0.0,
        "std": float(std_amount) if pd.notna(std_amount) else 0.0
    }

