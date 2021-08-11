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
        return self.apply_index(fill=True)

    
    @property
    def accounts(self):
        """
        All entries broken down to sub account.
        Useful for grouping entries by specific accounts.

        Returns:
            DataFrame: DataFrame with index ['account', 'sub_account', 'timestamp', 'type', 'symbol']
        """
        return self.apply_index(
            ['account', 'sub_account', 'timestamp', 'type', 'symbol'])

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
        summary = self.summarize()
        return summary['debit_value'].sum()

    @property
    def debit_quantity_sum(self):
        summary = self.summarize()
        return summary['debit_quantity'].sum()
    
    @property
    def credit_value_sum(self):
        summary = self.summarize()
        return summary['credit_value'].sum()
    
    @property
    def credit_quantity_sum(self):
        summary = self.summarize()
        return summary['credit_quantity'].sum()
    
    def add_entry(self, entry):
        self.entries.append(entry)

    def apply_index(self, index=['timestamp', 'id'], fill=False):
        ledger = self.raw
        if fill:
            ledger.fillna(0, inplace=True)
        ledger = self.raw.set_index(index)
        return ledger.sort_index()

    def summarize(self, index=['account', 'sub_account']):
        ledger = self.apply_index(index, fill=True)
        ledger = ledger.groupby(level=[0,1]).sum(numeric_only=False)
        return ledger

    def merge(self, ledgers):
        for l in ledgers:
            for e in l.entries:
                self.add_entry(e)
