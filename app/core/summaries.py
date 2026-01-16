import pandas as pd

def build_summarise(df):
    # Ensure correct types
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df['type'] = df['type'].astype(str)  # convert to string
    df['category'] = df['category'].astype(str)

    # Filter out rows with NaT or NaN
    df = df.dropna(subset=['date', 'amount', 'type'])

    # Monthly and yearly summaries
    monthly = df.groupby([df['date'].dt.to_period('M'), 'type'])['amount'].sum().unstack(fill_value=0)
    yearly = df.groupby([df['date'].dt.to_period('Y'), 'type'])['amount'].sum().unstack(fill_value=0)

    # Net cashflow
    monthly['net_cashflow'] = monthly.get('credit', 0) - monthly.get('debit', 0)
    yearly['net_cashflow'] = yearly.get('credit', 0) - yearly.get('debit', 0)

    # Trend
    monthly['trend'] = monthly['net_cashflow'].diff().fillna(0)
    yearly['trend'] = yearly['net_cashflow'].diff().fillna(0)

    # Profit per month
    profit_per_month = monthly['net_cashflow']

    return monthly, yearly, profit_per_month
