import pandas as pd

# This is the 'Contract'. Every Adapter must produce these columns.
REQUIRED_COLUMNS = [
    'Date', 
    'Account_ID', 
    'Debit', 
    'Credit', 
    'Segment', 
    'Dept', 
    'Currency', 
    'Transaction_ID'
]

def validate_schema(df: pd.DataFrame):
    """Checks if the dataframe meets the core engine requirements."""
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Dataframe is missing required core columns: {missing}")
    return True
