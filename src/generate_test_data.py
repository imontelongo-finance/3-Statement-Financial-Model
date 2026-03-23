import pandas as pd
import numpy as np
from datetime import datetime
import os

def generate_clean_data():
    os.makedirs("data/raw", exist_ok=True)
    years = range(2020, 2026)
    data = []
    base_rev = 1200000 
    
    for yr in years:
        date = datetime(yr, 12, 31)
        rev = base_rev * (1.18 ** (yr - 2020))
        
        # P&L: Account_ID, Debit, Credit
        data.append([date, 4100, 0, rev])            # Revenue (Credit)
        data.append([date, 5100, rev * 0.35, 0])       # COGS (Debit)
        data.append([date, 6100, rev * 0.25, 0])       # Salaries (Debit)
        data.append([date, 6200, rev * 0.10, 0])       # Mktg (Debit)
        data.append([date, 6300, rev * 0.05, 0])       # G&A (Debit)
        
        # BS:
        data.append([date, 1100, rev * 0.20, 0])       # Cash (Debit)
        data.append([date, 1200, rev * 0.08, 0])       # AR (Debit)
        data.append([date, 1600, 50000, 0])            # PP&E (Debit)
        data.append([date, 2600, 0, 100000])           # Debt (Credit)

    df = pd.DataFrame(data, columns=['Date', 'Account_ID', 'Debit', 'Credit'])
    df.to_csv("data/raw/erp_export_pro.csv", index=False)
    print("✅ Strategic Ledger Generated at data/raw/erp_export_pro.csv")

if __name__ == "__main__":
    generate_clean_data()