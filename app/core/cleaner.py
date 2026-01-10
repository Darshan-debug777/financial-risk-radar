import pandas as pd 

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df['date'] = pd.to_datetime(df['date'])
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df['type'] = df['type'].astype('category')
    df = df.drop_duplicates()
    return df