import pandas as pd
from io import BytesIO
from fastapi import APIRouter, UploadFile, File, HTTPException

from ..core.stats import compute_amount_stats
from ..core.summaries import build_summarise
from ..core.risk_engine import label_amount_risk
from ..core.categorizer import categorize_transaction
from ..core.cleaner import clean_dataframe

router = APIRouter()


def df_to_json_safe(df: pd.DataFrame):
    """Convert any DataFrame to JSON-safe list of dicts."""
    df = df.copy()
    df.reset_index(inplace=True, drop=True)
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].astype(str)
        elif pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].astype(float)
        else:
            df[col] = df[col].astype(str)
    return df.to_dict(orient="records")


@router.post("/upload/TRANSACTIONS/file")
async def upload_csv(file: UploadFile = File(...)):

    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Upload a CSV file.")

    try:
        content = await file.read()
        df = pd.read_csv(BytesIO(content))
        print("CSV columns detected:", df.columns.tolist())  # Debug for hackathon

        
        df = clean_dataframe(df)

        
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        if 'amount' in df.columns:
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        if 'type' in df.columns:
            df['type'] = df['type'].astype(str)
        if 'description' in df.columns:
            df['category'] = df['description'].apply(categorize_transaction)

        
        essential_cols = [c for c in ['date', 'amount', 'type'] if c in df.columns]
        if essential_cols:
            df = df.dropna(subset=essential_cols)

        
        if 'amount' in df.columns:
            amount_stats = compute_amount_stats(df)
            df = label_amount_risk(df, amount_stats['mean'], amount_stats['std'])
        

        total_transactions = len(df)

        total_credit = 0.0
        total_debit = 0.0
        average_amount = 0.0

        if 'type' in df.columns and 'amount' in df.columns:
            total_credit = df.loc[df['type'].str.lower() == 'credit', 'amount'].sum()
            total_debit = df.loc[df['type'].str.lower() == 'debit', 'amount'].sum()
            average_amount = df['amount'].mean()

        precomputed_metrics = {
            "total_transactions": total_transactions,
            "total_credit": float(total_credit),
            "total_debit": float(total_debit),
            "average_amount": float(average_amount)
        }
      
        
        if all(col in df.columns for col in ['date', 'amount', 'type']):
            monthly, yearly, profit_per_month = build_summarise(df)
        else:
            monthly, yearly, profit_per_month = pd.DataFrame(), pd.DataFrame(), {}

        
        if all(col in df.columns for col in ['type', 'amount']):
            total_credit = df.loc[df['type'].str.lower() == 'credit', 'amount'].sum()
            total_debit = df.loc[df['type'].str.lower() == 'debit', 'amount'].sum()
            cashflow_status = "positive" if total_credit > total_debit else "negative"
        else:
            cashflow_status = "unknown"

        return {
    "cashflow_status": cashflow_status,
    "monthly_summary": df_to_json_safe(monthly),
    "yearly_summary": df_to_json_safe(yearly),
    "profit_per_month": {str(k): float(v) for k, v in profit_per_month.items()},
    "metrics": precomputed_metrics  
}

    except Exception as e:
      
        raise HTTPException(status_code=500, detail=f"Failed to process file: {e}")
    




        