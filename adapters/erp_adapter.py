import pandas as pd
import sys
import os

# Adding project root to path so we can import core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.schema import validate_schema

def map_raw_to_core(raw_df: pd.DataFrame):
    """
    Translates messy ERP-specific columns to our Universal 7-Column Schema.
    Modify the dictionary below based on the ERP export (NetSuite, SAP, etc.)
    """
    mapping = {
        'G_L_AccountNumber': 'Account_ID',
        'Posting_Date': 'Date',
        'Amount_DR': 'Debit',
        'Amount_CR': 'Credit',
        'Region_Code': 'Segment',
        'Cost_Center': 'Dept',
        'Local_Currency': 'Currency',
        'Voucher_ID': 'Transaction_ID'
    }
    
    # Rename columns and select only the core 7
    core_df = raw_df.rename(columns=mapping)
    
    # Ensure all required columns exist (add placeholders if missing in ERP)
    for col in ['Debit', 'Credit']:
        if col not in core_df.columns:
            core_df[col] = 0.0
            
    # Cast types for calculation safety
    core_df['Date'] = pd.to_datetime(core_df['Date'])
    core_df[['Debit', 'Credit']] = core_df[['Debit', 'Credit']].fillna(0).astype(float)
    
    validate_schema(core_df)
    return core_df[
        ['Date', 'Account_ID', 'Debit', 'Credit', 'Segment', 'Dept', 'Currency', 'Transaction_ID']
    ]
