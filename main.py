import pandas as pd
from src.generate_test_data import generate_erp_dump
from adapters.erp_adapter import map_raw_to_core
from core.engine import FinanceEngine

def run_pipeline():
    print("🚀 Starting Finance Engine Pipeline...")

    # 1. DATA INGESTION
    # In a real company, this replaces the manual ERP export process
    generate_erp_dump("data/raw/erp_export_march.csv")
    raw_df = pd.read_csv("data/raw/erp_export_march.csv")
    print(f"📥 Loaded {len(raw_df)} raw transactions from ERP.")

    # 2. ADAPTATION (The Translation Layer)
    # Maps messy ERP columns to our 7-column 'Standard Contract'
    clean_df = map_raw_to_core(raw_df)
    print("✅ Data successfully adapted to Core Schema.")

    # 3. CHART OF ACCOUNTS (The Logic Map)
    # This defines how IDs roll up into the 3 Statements
    coa_data = {
        'Account_ID': [11010, 12010, 21010, 41010, 51010, 61010],
        'Account_Name': ['Cash', 'Accounts Receivable', 'Accounts Payable', 'SaaS Revenue', 'Cloud Hosting', 'Operating Expense'],
        'Category': ['Cash & Equiv', 'Current Assets', 'Current Liabilities', 'Revenue', 'COGS', 'OpEx'],
        'Statement_Type': ['BS', 'BS', 'BS', 'PL', 'PL', 'PL']
    }
    coa_df = pd.DataFrame(coa_data)

    # 4. CORE ENGINE EXECUTION
    engine = FinanceEngine(clean_df, coa_df)

    # 5. VALIDATION (The Hard Close)
    audit = engine.validate_trial_balance()
    if audit['Is_Balanced']:
        print(f"⚖️  Audit Passed: Debits/Credits balance at ${audit['Debits']:,.2f}")
    else:
        print(f"❌ Audit Failed: Discrepancy of ${audit['Difference']}")

    # 6. REPORTING
    print("\n" + "="*50)
    print("SEGMENTED P&L REPORT (USD Millions)")
    print("="*50)
    
    # Let's scale the numbers for readability (Millions)
    pl_report = engine.get_segmented_pl() / 1_000_000
    print(pl_report.round(2))
    
    print("\n" + "="*50)
    print("CONSOLIDATED BALANCE SHEET")
    print("="*50)
    bs_report = engine.get_consolidated_bs()
    print(bs_report)

if __name__ == "__main__":
    run_pipeline()