import pandas as pd
import numpy as np

class FinanceEngine:
    def __init__(self, core_df, coa_df):
        # Merge Ledger with Chart of Accounts
        self.ledger = core_df.merge(coa_df, on='Account_ID')

    def get_model_results(self, drivers):
        # 1. Sign Correction Logic
        self.ledger['Value'] = np.where(self.ledger['Statement_Type'] == 'PL',
                                        np.where(self.ledger['Category'] == 'Revenue', 
                                                 self.ledger['Credit'] - self.ledger['Debit'], 
                                                 self.ledger['Debit'] - self.ledger['Credit']),
                                        np.where(self.ledger['Category'].isin(['Asset', 'Fixed Asset']),
                                                 self.ledger['Debit'] - self.ledger['Credit'], 
                                                 self.ledger['Credit'] - self.ledger['Debit']))
        
        pivot = self.ledger.pivot_table(index=['Statement_Type', 'Category', 'Account_Name'], 
                                        columns=self.ledger['Date'].dt.year, 
                                        values='Value', aggfunc='sum').fillna(0)

        # 2. Forecasting (2026-2028)
        years = [2026, 2027, 2028]
        for yr in years:
            # FIX: Carry forward previous year's BS values to prevent NaN (€nan)
            if 'BS' in pivot.index.get_level_values(0):
                pivot.loc['BS', yr] = pivot.loc['BS', yr-1].values
            
            # P&L Projections
            prev_rev = pivot.loc[('PL', 'Revenue', 'Revenue'), yr-1]
            rev_proj = prev_rev * (1 + drivers['rev_growth'])
            pivot.loc[('PL', 'Revenue', 'Revenue'), yr] = rev_proj
            
            pivot.loc[('PL', 'Cost of Sales', 'COGS'), yr] = rev_proj * 0.35 * (1 + drivers['cogs_eff'])
            pivot.loc[('PL', 'OpEx', slice(None)), yr] = pivot.loc[('PL', 'OpEx', slice(None)), yr-1].values * (1 + drivers['opex_scale'])
            
            ebitda = rev_proj - pivot.loc[('PL', 'Cost of Sales', 'COGS'), yr] - pivot.loc[('PL', 'OpEx', slice(None)), yr].sum()
            ni = ebitda * (1 - drivers['tax_rate'])
            
            # BS Updates
            pivot.loc[('BS', 'Asset', 'Cash'), yr] = pivot.loc[('BS', 'Asset', 'Cash'), yr-1] + ni
            if ('BS', 'Asset', 'AR') in pivot.index:
                pivot.loc[('BS', 'Asset', 'AR'), yr] = rev_proj * 0.08

        # 3. Income Statement Construction
        pl = pivot.loc['PL'].copy()
        rev = pl.loc[('Revenue', 'Revenue')]
        cogs = pl.loc[('Cost of Sales', 'COGS')]
        ebitda = rev - cogs - pl.loc[('OpEx', slice(None))].sum()
        
        pl.loc[('Metrics', 'Gross Margin %'), :] = ((rev - cogs) / rev * 100)
        pl.loc[('Metrics', 'EBITDA Margin %'), :] = (ebitda / rev * 100)
        pl.loc[('Subtotals', 'EBITDA Value'), :] = ebitda
        pl.loc[('Subtotals', 'Net Income'), :] = ebitda * (1 - drivers['tax_rate'])

        # 4. Cash Flow Statement
        cf = pd.DataFrame(index=['Net Income', 'Adj: Change in AR', 'Net Cash Flow'], columns=pl.columns)
        cf.loc['Net Income'] = pl.loc[('Subtotals', 'Net Income')]
        if ('BS', 'Asset', 'AR') in pivot.index:
            cf.loc['Adj: Change in AR'] = -(pivot.loc[('BS', 'Asset', 'AR')].diff().fillna(0))
        cf.loc['Net Cash Flow'] = cf.sum()

        # 5. Advanced Analytics (Runway & Efficiency)
        cash = pivot.loc[('BS', 'Asset', 'Cash')]
        rev_growth_pct = rev.pct_change().fillna(0) * 100
        ebitda_margin = pl.loc[('Metrics', 'EBITDA Margin %')]
        
        # Rule of 40: Growth + Profitability
        rule_of_40 = rev_growth_pct + ebitda_margin
        
        # Runway: Cash / Monthly Net Loss
        monthly_burn = (cf.loc['Net Cash Flow'] / 12).apply(lambda x: abs(x) if x < 0 else 0)
        runway = (cash / monthly_burn).replace([np.inf, -np.inf], 99).fillna(99)

        analytics_df = pd.DataFrame({
            'Revenue Growth %': rev_growth_pct.values,
            'EBITDA Margin %': ebitda_margin.values,
            'Rule of 40 %': rule_of_40.values,
            'Monthly Net Burn': monthly_burn.values,
            'Runway (Months)': runway.values,
            'Ending Cash': cash.values
        }, index=rev.index.astype(str)).T

        # 6. Headcount
        total_fte = (rev.abs() / 150000).round(0).clip(lower=1)
        hc_plan = pd.DataFrame({
            'FTE Count': total_fte.values, 
            'Personnel Cost': (total_fte * 90000).values
        }, index=rev.index.astype(str)).T

        return pl, pivot.loc['BS'], cf, analytics_df, hc_plan