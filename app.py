import streamlit as st
import pandas as pd
import numpy as np
import os
import sys

# 1. Standardize pathing for Cloud environment
root_path = os.path.dirname(os.path.abspath(__file__))
if root_path not in sys.path:
    sys.path.append(root_path)

# 2. Add 'src' to path so generate_test_data can be found
src_path = os.path.join(root_path, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

# 3. Imports from your subfolders
from core.engine import FinanceEngine
try:
    from generate_test_data import generate_clean_data
except ImportError:
    st.error("Deployment Error: 'generate_test_data.py' not found in /src folder.")

# --- PAGE CONFIG ---
st.set_page_config(page_title="Strategic Finance Engine | Berlin Ops", layout="wide")

@st.cache_data
def load_data():
    # Create the directory structure if it doesn't exist (Cloud requirement)
    if not os.path.exists("data/raw"):
        os.makedirs("data/raw")
        
    data_path = "data/raw/erp_export_pro.csv"
    
    # Generate data if missing
    if not os.path.exists(data_path):
        try:
            generate_clean_data()
        except Exception as e:
            st.error(f"Data generation failed: {e}")
            return pd.DataFrame(), pd.DataFrame()
        
    raw = pd.read_csv(data_path, parse_dates=['Date'])
    
    # Chart of Accounts Mapping
    coa = pd.DataFrame({
        'Account_ID': [1100, 1200, 1600, 2600, 3100, 4100, 5100, 6100, 6200, 6300],
        'Account_Name': ['Cash', 'AR', 'PP&E', 'Debt', 'Ret. Earnings', 'Revenue', 'COGS', 'Salaries', 'Mktg', 'G&A'],
        'Category': ['Asset', 'Asset', 'Fixed Asset', 'Liab', 'Equity', 'Revenue', 'Cost of Sales', 'OpEx', 'OpEx', 'OpEx'],
        'Statement_Type': ['BS', 'BS', 'BS', 'BS', 'BS', 'PL', 'PL', 'PL', 'PL', 'PL']
    })
    return raw, coa

# --- SMART FORMATTING ---
def format_df(df):
    formatted = df.copy().astype(object)
    for row in df.index:
        row_label = str(row)
        is_pct = any(x in row_label for x in ["%", "Rule of 40", "Growth"])
        for col in df.columns:
            val = df.loc[row, col]
            if pd.isna(val):
                formatted.loc[row, col] = "0.0%" if is_pct else "€0"
            elif is_pct:
                formatted.loc[row, col] = f"{val:.1f}%"
            elif "Runway" in row_label or "Count" in row_label:
                formatted.loc[row, col] = f"{val:.1f}"
            else:
                formatted.loc[row, col] = f"€{val:,.0f}"
    return formatted

# --- EXECUTION ---
data, coa = load_data()

if not data.empty:
    st.sidebar.title("🛠️ Operational Drivers")
    drivers = {
        'rev_growth': st.sidebar.slider("Revenue Growth %", -10, 100, 25) / 100,
        'cogs_eff': st.sidebar.slider("COGS Efficiency %", -20, 20, 0) / 100,
        'opex_scale': st.sidebar.slider("OpEx Scaling %", 0, 50, 15) / 100,
        'tax_rate': st.sidebar.number_input("Tax Rate %", value=30) / 100
    }

    engine = FinanceEngine(data, coa)
    pl, bs, cf, analytics, hc = engine.get_model_results(drivers)

    st.title("3-Statement Financial Model")
    t1, t2, t3 = st.tabs(["📊 Financial Statements", "📈 Runway & Efficiency", "👥 Headcount"])

    with t1:
        st.subheader("I. Income Statement")
        st.dataframe(format_df(pl), use_container_width=True)
        st.subheader("II. Balance Sheet")
        st.dataframe(format_df(bs), use_container_width=True)
        st.subheader("III. Statement of Cash Flows")
        st.dataframe(format_df(cf), use_container_width=True)

    with t2:
        st.subheader("Runway & Efficiency Metrics")
        st.dataframe(format_df(analytics), use_container_width=True)

    with t3:
        st.subheader("Headcount Hiring Plan")
        st.dataframe(format_df(hc), use_container_width=True)