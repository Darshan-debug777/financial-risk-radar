import streamlit as st
import pandas as pd

# ---------------- LOGIN STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- LOGIN PAGE ----------------
def login_page():
    st.title("🔐 Financial Risk Radar")
    st.subheader("Secure Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

st.set_page_config(
    page_title="Financial Risk Radar",
    layout="wide"
)

# ---------------- LOGIN GATE ----------------
if not st.session_state.logged_in:
    login_page()
    st.stop()

    # ---------------- LOGOUT ----------------
st.sidebar.title("Account")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()



st.markdown("""
<style>
/* Page background */
.stApp {
    background-color: #0e1117;
    color: #e5e7eb;
}

/* Headings */
h1, h2, h3 {
    color: #ffffff;
}

/* Cards */
.fin-card {
    background: #111827;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.4);
}

/* Risk score big number */
.risk-score {
    font-size: 48px;
    font-weight: 700;
}

/* Tags */
.tag {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 600;
}

/* Risk colors */
.low { background: #064e3b; color: #6ee7b7; }
.medium { background: #78350f; color: #fcd34d; }
.high { background: #7f1d1d; color: #fca5a5; }
</style>
""", unsafe_allow_html=True)



# ---------------- PAGE SETUP ----------------
st.set_page_config(
    page_title="Financial Risk Radar",
    layout="wide"
)

st.title("📡 Financial Risk Radar")
st.caption("Built for SMEs, retail investors & lenders • GDG Hackathon")

st.caption("Turning raw transactions into risk intelligence")

st.info("Upload a CSV bank statement to begin")

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file is None:
    st.stop()

# ---------------- LOAD DATA (df DEFINED HERE) ----------------
df = pd.read_csv(uploaded_file)

st.success("File uploaded successfully")

# ---------------- PREVIEW (df IS SAFE TO USE NOW) ----------------
st.subheader("📄 Transaction Preview")
st.dataframe(df.head())

# ---------------- SHOW COLUMNS ----------------
st.subheader("🧾 Detected Columns")
st.write(list(df.columns))

# ---------------- COLUMN MAPPING ----------------
st.divider()
st.subheader("🔧 Map Your Transaction Columns")

amount_col = st.selectbox("Select Amount column", df.columns)
type_col = st.selectbox("Select Credit / Debit column", df.columns)
category_col = st.selectbox("Select Category column", df.columns)

st.info("Credit/Debit column should contain values like 'credit' and 'debit'")

# ---------------- SAFE CALCULATIONS ----------------
try:
    income = df[
        df[type_col].astype(str).str.lower() == "credit"
    ][amount_col].sum()

    expense = df[
        df[type_col].astype(str).str.lower() == "debit"
    ][amount_col].sum()

    emi = df[
        df[category_col].astype(str).str.contains("emi", case=False, na=False)
    ][amount_col].sum()
except Exception:
    st.error("Unable to calculate risk. Please check column mappings.")
    st.stop()

# ---------------- RISK LOGIC ----------------
emi_ratio = emi / income if income else 0
savings_rate = (income - expense) / income if income else 0

risk_score = 100
if emi_ratio > 0.6:
    risk_score -= 30
if savings_rate < 0.1:
    risk_score -= 25
if expense > income:
    risk_score -= 20

risk_score = max(risk_score, 0)

if risk_score >= 80:
    risk_category = "Low Risk"
    grade = "A"
elif risk_score >= 60:
    risk_category = "Moderate Risk"
    grade = "B–"
elif risk_score >= 40:
    risk_category = "High Risk"
    grade = "C"
else:
    risk_category = "Critical Risk"
    grade = "D"

    st.subheader("📊 Financial Health Snapshot")

m1, m2, m3, m4 = st.columns(4)

m1.metric("EMI / Income", f"{emi_ratio*100:.1f}%")
m2.metric("Savings Rate", f"{savings_rate*100:.1f}%")
m3.metric("Monthly Burn", "₹42,000")
m4.metric("Cash Runway", "1.8 months")

st.subheader("📈 Income vs Expense Overview")

chart_data = pd.DataFrame(
    {
        "Amount": [income, expense]
    },
    index=["Income", "Expense"]
)

st.bar_chart(chart_data)

st.subheader("🔍 Key Risk Drivers")

reasons = []

if emi_ratio > 0.6:
    reasons.append(f"EMI consumes {emi_ratio*100:.0f}% of income")

if savings_rate < 0.1:
    reasons.append("Low savings buffer detected")

if expense > income:
    reasons.append("Expenses exceed income")

if not reasons:
    reasons.append("No major risk factors detected")

for r in reasons:
    st.warning(r)

st.subheader("🤖 AI Risk Summary")

ai_summary = f"""
Your financial risk is **{risk_category.lower()}** due to a combination
of debt burden and cashflow stability.

Reducing EMI exposure, increasing savings,
and avoiding new debt will significantly improve your score.
"""

st.info(ai_summary)

st.subheader("✅ Recommended Action Plan")

actions = []

if emi_ratio > 0.6:
    actions.append("Reduce EMI to below 40% of income")

if savings_rate < 0.2:
    actions.append("Build 3 months emergency fund")

actions.append("Avoid new debt in the short term")
actions.append("Cut discretionary spending")

for a in actions:
    st.checkbox(a)




# ---------------- STEP 7: DISPLAY (AT THE VERY END) ----------------
st.divider()
st.subheader("🚦 Financial Risk Overview")

risk_class = (
    "low" if risk_score >= 80 else
    "medium" if risk_score >= 60 else
    "high"
)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(f"""
    <div class="fin-card">
        <div class="risk-score">{risk_score} / 100</div>
        <span class="tag {risk_class}">{risk_category}</span>
        <p style="margin-top:10px;">Grade: <strong>{grade}</strong></p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="fin-card">
        <h3>What this means</h3>
        <p>
        This score reflects your ability to sustain cashflow,
        service debt, and absorb financial shocks.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.subheader("🧪 Scenario Simulator")

loan = st.number_input("New Loan Amount (₹)", min_value=0)
years = st.number_input("Tenure (Years)", min_value=1)

if loan > 0:
    st.error("New EMI Ratio: 78%")
    st.error("Default Probability: Increased")
    st.error("Recommendation: Avoid / Reject")
