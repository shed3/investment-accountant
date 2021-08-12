"""
The Ledger consumes accounting journal entries and manipulates 
those entries within a pandas dataframe. The Ledger provides a 
simple interface for organizing data into common accounting structures.

The Ledger's main role is to act as the general ledger for the book keeper.

  Typical usage example:
    entry = {...}
    ledger = Ledger()
    ledger.add_entry(entry)
    summary = ledger.summarize()
"""
import pandas as pd
import numpy as np

class Ledger:

    def __init__(self) -> None:

        self.entries = []

    @property
    def raw(self):
        """
        All entries grouped by timestamp and id.
        Useful for ordering chronological. 

        Returns:
            DataFrame: Unindexed DataFrame
        """
        if len(self.entries) > 0:
            return pd.DataFrame(self.entries)
        return pd.DataFrame()

        # rename columns even if empty.

    @property
    def simple(self):
        """
        Values from self.raw with na values filled

        Returns:
            DataFrame: DataFrame with index ['timestamp', 'id']
        """
        return self.apply_index(self.raw, fill=True)

    
    @property
    def accounts(self):
        """
        All entries broken down to sub account.
        Useful for grouping entries by specific accounts.

        Returns:
            DataFrame: DataFrame with index ['account', 'sub_account', 'timestamp', 'type', 'symbol']
        """
        return self.apply_index(self.simple, 
            ['account_type', 'account', 'sub_account', 'timestamp', 'type', 'symbol'])

    @property
    def symbols(self):
        """
        All symbols that appear in entries.

        Returns:
            list: A list containing the capitalized symbols.
        """
        return np.unique(np.array(self.simple['symbol'].tolist()))

    @property
    def debit_value_sum(self):
        summary = self.summarize(self.simple)
        return summary['debit_value'].sum()

    @property
    def debit_quantity_sum(self):
        summary = self.summarize(self.simple)
        return summary['debit_quantity'].sum()
    
    @property
    def credit_value_sum(self):
        summary = self.summarize(self.simple)
        return summary['credit_value'].sum()
    
    @property
    def credit_quantity_sum(self):
        summary = self.summarize(self.simple)
        return summary['credit_quantity'].sum()
    
    def add_entry(self, entry):
        self.entries.append(entry)

    def apply_index(self, ledger, index=['timestamp'], fill=False,):
        ledger.reset_index(inplace=True)
        if fill:
            ledger.fillna(0, inplace=True)
        ledger.set_index(index, inplace=True)
        return ledger.sort_index()

    def summarize(self, ledger, index=['account_type', 'account', 'sub_account']):
        ledger = self.apply_index(ledger, index, fill=True)
        ledger = ledger.groupby(level=-1).sum(numeric_only=False)
        ledger = self.add_balance(ledger)
        return ledger

    def add_balance(self, ledger):
        ledger['debit_balance'] = ledger['debit_value'] - ledger['credit_value']
        ledger['credit_balance'] = ledger['credit_value'] - ledger['debit_value']
        ledger['debit_balance_quantity'] = ledger['debit_quantity'] - ledger['credit_quantity']
        ledger['credit_balance_quantity'] = ledger['credit_quantity'] - ledger['debit_quantity']        
        if 'account_type' in ledger.columns:
            ledger['balance'] = ledger['credit_balance'].where(ledger['account_type'] != 'assets', ledger['debit_balance'])
            ledger['balance_quantity'] = ledger['credit_balance_quantity'].where(ledger['account_type'] != 'assets', ledger['debit_balance_quantity'])
        if ledger.index.nlevels > 1:
            if 'account_type' in ledger.index._names:
                ledger['balance'] = ledger['credit_balance'].where(ledger.index.get_level_values(level='account_type') != 'assets', ledger['debit_balance'])
                ledger['balance_quantity'] = ledger['credit_balance_quantity'].where(ledger.index.get_level_values(level='account_type') != 'assets', ledger['debit_balance_quantity'])      
        else:
            if 'account_type' in ledger.index.name:
                ledger['balance'] = ledger['credit_balance'].where(ledger.index.get_level_values(level='account_type') != 'assets', ledger['debit_balance'])
                ledger['balance_quantity'] = ledger['credit_balance_quantity'].where(ledger.index.get_level_values(level='account_type') != 'assets', ledger['debit_balance_quantity'])                   
        return ledger

    def add_running_total(self, ledger):
        # DO NOT INCLUDE TIMESTAMP IN INDEX
        ledger = self.add_balance(ledger)
        sort_val = []
        if ledger.index.nlevels > 1:
            sort_val += ledger.index._names
        else:
            sort_val.append(ledger.index.name)
        sort_val.append('timestamp')
        ledger = ledger.sort_values(sort_val)

        ledger['running_bal'] = ledger.groupby(level=-1)['balance'].apply(lambda x: x.cumsum())
        ledger['running_bal_quantity'] = ledger.groupby(level=-1)['balance_quantity'].apply(lambda x: x.cumsum())



        # ledger['balance'] = ledger['account_type'].apply(lambda x: ledger['debit_balance'] if x == 'assets' else (ledger['credit_value'] - ledger['debit_value']))
        # ledger['balance_quantity'] = ledger['credit_quantity'] - ledger['debit_quantity']
        # ledger['balance_quantity'] = ledger['balance'].apply(lambda x: ledger['debit_quantity'] - ledger['credit_quantity'] if ledger['account_type'] == 'assets' else x)
        return ledger

    def merge(self, ledgers):
        for l in ledgers:
            for e in l.entries:
                self.add_entry(e)
