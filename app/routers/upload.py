import pandas as pd
from io import BytesIO
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any

from ..core.stats import compute_amount_stats
from ..core.summaries import build_summarise
from ..core.risk_engine import label_amount_risk
from ..core.categorizer import categorize_transaction
from ..core.cleaner import clean_dataframe
from ..core.gemini_client import generate_text, GeminiError

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
async def upload_csv(file: UploadFile = File(...)) -> Dict[str, Any]:
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Upload a CSV file.")

    try:
        content = await file.read()
        df = pd.read_csv(BytesIO(content))
        print("CSV columns detected:", df.columns.tolist())  # Debug

        # Basic cleaning and types
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

        # Precompute amount stats and label risk
        if 'amount' in df.columns:
            amount_stats = compute_amount_stats(df)
            df = label_amount_risk(df, amount_stats['mean'], amount_stats['std'])
        else:
            amount_stats = {"mean": 0.0, "std": 0.0}

        # Basic precomputed metrics
        total_transactions = len(df)
        total_credit = 0.0
        total_debit = 0.0
        average_amount = 0.0

        if 'type' in df.columns and 'amount' in df.columns:
            total_credit = df.loc[df['type'].str.lower() == 'credit', 'amount'].sum()
            total_debit = df.loc[df['type'].str.lower() == 'debit', 'amount'].sum()
            average_amount = float(df['amount'].mean())

        precomputed_metrics = {
            "total_transactions": int(total_transactions),
            "total_credit": float(total_credit),
            "total_debit": float(total_debit),
            "average_amount": float(average_amount)
        }

        # Summaries if possible
        if all(col in df.columns for col in ['date', 'amount', 'type']):
            monthly, yearly, profit_per_month = build_summarise(df)
        else:
            monthly, yearly, profit_per_month = pd.DataFrame(), pd.DataFrame(), {}

        # Cashflow status
        if all(col in df.columns for col in ['type', 'amount']):
            total_credit = df.loc[df['type'].str.lower() == 'credit', 'amount'].sum()
            total_debit = df.loc[df['type'].str.lower() == 'debit', 'amount'].sum()
            cashflow_status = "positive" if total_credit > total_debit else "negative"
        else:
            cashflow_status = "unknown"

        # LLM enrichment (Gemini): explain top N high-risk transactions
        df['llm_note'] = ""
        max_enrich = 5  # limit number of LLM calls per upload to control cost
        enriched = 0

        if 'amount_risk' in df.columns:
            high_risk_rows = df[df['amount_risk'] == 'High Risk']
            for idx, row in high_risk_rows.iterrows():
                if enriched >= max_enrich:
                    break
                desc = str(row.get('description', ''))
                amt = row.get('amount', '')
                ttype = row.get('type', '')
                prompt = (
                    "You are a financial analyst. Explain succinctly why the following transaction "
                    "might be considered high risk. Mention possible flags or checks an analyst should perform.\n\n"
                    f"Description: {desc}\nAmount: {amt}\nType: {ttype}\n\nResponse:"
                )
                try:
                    note = generate_text(prompt, max_tokens=256)
                    df.at[idx, 'llm_note'] = note
                except GeminiError as ge:
                    # keep going but record the error in the row
                    df.at[idx, 'llm_note'] = f"LLM error: {ge}"
                except Exception as e:
                    df.at[idx, 'llm_note'] = f"LLM unexpected error: {e}"
                enriched += 1

        response = {
            "cashflow_status": cashflow_status,
            "monthly_summary": df_to_json_safe(monthly),
            "yearly_summary": df_to_json_safe(yearly),
            "profit_per_month": {str(k): float(v) for k, v in profit_per_month.items()},
            "metrics": precomputed_metrics,
            # include only first N enriched rows for speed
            "enriched_sample": df[df['llm_note'] != ""].head(20).to_dict(orient="records")
        }

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {e}")
