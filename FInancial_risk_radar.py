import pandas as pd         
#python -m uvicorn app.main:app --reload
                  
def load_csv(path):               #uvicorn app.main:app --reload

    df = pd.read_csv(path)
    df.date = pd.to_datetime(df.date)
    df.amount = pd.to_numeric(df.amount, errors='coerce')
    df.type = df.type.astype('category')
    return df

df = load_csv("C:\\Users\\Darshan jain\\OneDrive\\Desktop\\financial risk radar backend\\TRANSACTION.csv")
print(df.head(100))
print(df.columns)
print(df.dtypes)

empty_count = df.isnull().sum().sum()
print("Number of missing values in the dataset:", empty_count)

duplicate_counts = df.duplicated().sum()
print("Number of duplicate rows in the dataset:", duplicate_counts)

df = df.drop_duplicates()
print("Dataset shape after removing duplicates:", df.shape)

null_per_columns = df.isnull().sum()
print("Number of null values in each column:\n", null_per_columns)

mean_amount = df['amount'].mean()
std_amount = df['amount'].std()
print("Average transaction amount:", mean_amount)
print("Standard deviation of transaction amount:", std_amount)

high_threshold = mean_amount + 2 * std_amount 
medium_threshold = mean_amount + std_amount
low_threshold = mean_amount + 0.5 * std_amount

def high_risk_label(amount):
    if amount >= high_threshold:
        return 'High Risk'
    elif amount >= medium_threshold:
        return 'Medium Risk'
    elif amount >= low_threshold:
        return 'Low Risk'
    else:
        return 'Normal'

df['amount_risk'] = df['amount'].apply(high_risk_label)
print(df[['amount', 'amount_risk']].head(100))
credit_amount = df[df['type'] == 'credit']['amount']
debit_amount = df[df['type'] == 'debit']['amount']
credit_mean = credit_amount.mean()
debit_mean = debit_amount.mean()
def cashflow_analysis(credit_mean, debit_mean):
    if credit_mean > debit_mean:
        return 'positive cashflow'
    elif credit_mean < debit_mean:
        return 'negative cashflow'
    else:
        return "neutral cashflow"

cashflow = cashflow_analysis(credit_mean, debit_mean)
print("Cashflow status:", cashflow)     

total_credit = credit_amount.sum()
total_debit = debit_amount.sum()    
net_cashflow = total_credit - total_debit
print("Net cashflow:", net_cashflow)
print("Total credit amount:", total_credit)
print("Total debit amount:", total_debit)

monthly_summary = (
    df.groupby([df.date.dt.to_period("M"),'type'], observed=True)['amount']
    .sum()
    .unstack()
    .fillna(0)
)
print("Monthly\nSummary", monthly_summary)

profit_per_month = monthly_summary['net_cashflow'] = monthly_summary['credit'] - monthly_summary['debit']
print("Profit per month:\n", profit_per_month)

yearly_summary = (
    df.groupby([df.date.dt.to_period("Y"),'type'], observed=True)['amount']
    .sum()
    .unstack()
    .fillna(0)
)
print("Yearly Summary", yearly_summary)

def bank_transaction_categories(description):
    description = str(description).lower()
    if 'salary' in description or 'payroll' in description:
        return 'Income'
    elif 'grocery' in description or 'supermarket' in description:
        return 'Groceries'
    elif 'rent' in description or 'mortgage' in description:
        return 'Housing'
    elif 'restaurant' in description or 'cafe' in description:
        return 'Dining'
    elif 'entertainment' in description or 'movie' in description:
        return 'Entertainment'
    elif 'utilities' in description or 'electricity' in description or 'water' in description:
        return 'Utilities'
    elif 'transportation' in description or 'fuel' in description or 'taxi' in description:
        return 'Transportation'
    elif 'health' in description or 'pharmacy' in description:
        return 'Healthcare'
    elif 'upi' in description or 'bank transfer' in description:
        return 'UPI Payments'
    elif 'client' in description or 'project' in description:
        return 'Business'
    else:
        return 'Other'
    
df['category'] = df['description'].apply(bank_transaction_categories)
print("Transactions with Categories:\n", df[['description', 'category']].head(100))

daily_summary = df.groupby([df.date.dt.to_period("D"), 'category'], observed=True)['amount'].sum().unstack().fillna(0)
print("Daily Summary:\n", daily_summary)
weekly_summary = df.groupby([df.date.dt.to_period("W"), 'category'], observed=True)['amount'].sum().unstack().fillna(0)
print("Weekly Summary:\n", weekly_summary)

df.to_csv("TRANSACTION_ANALYZED.csv", index=False)

monthly_summary['net_cashflow'] =monthly_summary['credit'] - monthly_summary['debit']
monthly_summary['trend'] = monthly_summary['net_cashflow'].diff().fillna(0)
print("Monthly Summary with Trends:\n", monthly_summary[['net_cashflow','trend']])  
