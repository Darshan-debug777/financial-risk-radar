

import pandas as pd

def label_amount_risk(df: pd.DataFrame, mean_amount: float, std_amount: float) -> pd.DataFrame:
    """
    Labels each transaction in the 'amount' column as:
    'High Risk', 'Medium Risk', 'Low Risk', or 'Normal'
    based on mean and standard deviation.
    """
    if 'amount' not in df.columns:
        df['amount_risk'] = "Unknown"
        return df

    high_threshold = mean_amount + 2 * std_amount
    medium_threshold = mean_amount + std_amount
    low_threshold = mean_amount + 0.5 * std_amount

    def risk_label(amount):
        if pd.isna(amount):
            return "Unknown"
        if amount >= high_threshold:
            return "High Risk"
        elif amount >= medium_threshold:
            return "Medium Risk"
        elif amount >= low_threshold:
            return "Low Risk"
        else:
            return "Normal"

    df['amount_risk'] = df['amount'].apply(risk_label)
    return df
