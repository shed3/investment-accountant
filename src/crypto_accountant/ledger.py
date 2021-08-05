"""This module is for accounts and contains the base functions that control their balances and entries.

An account represents a single account for tracking transactions. Transactions may affect one or multiple accounts. 

  Typical usage example:

    cash = Acct(('Assets', 'Cash'), 'Asset', 'USD') 
    cash.inc(125.99, 125.99, 'Sell, 'Coinbase', datetime.datetime.now()) 
    cash.dec(40, 40, 'Buy, 'Coinbase', datetime.datetime.now()) 
"""
import re
import logging
import pandas as pd
import numpy as np
from .utils import is_row_valid

log = logging.getLogger(__name__)


class Ledger:
    """
    Basic financial account which can be credited and debited, and contains its own ledger.

    Accounts can be created with an inital set of keys, which will be added on every transaction in that account.
    Additionally, when logging transactions you may pass an arbitrary number of child accounts for further breakdowns.
    If you want to pass something that is not a breakdown, it may be better to use a new account. For example, to 
    differentiate positions bought with credit versus cash, it is probable not best to add a credit key, instead making
    a new account that tracks credit, which can then be broken down the same way as the original account. This needs 
    working based on DF manipulation results.    
    """

    def __init__(self) -> None:

        self.entries = []
        self.debits = []
        self.processed = False

    @property
    def raw_ledger(self):
        """All transactions grouped by timestamp, type, and symbol. Useful for looking at all journal entries in order. Base ledger for every other operation.

        Returns:
            DataFrame: DataFrame with index ['timestamp', 'id']
        """
        if len(self.entries) > 0:
            return pd.DataFrame(self.entries)
        return pd.DataFrame()

        # rename columns even if empty.


    @property
    def ledger(self):
        """All transactions grouped by timestamp, type, and symbol. Useful for looking at all journal entries in order. Base ledger for every other operation.

        Returns:
            DataFrame: DataFrame with index ['timestamp', 'id']
        """
        return self.set_ledger_index(['timestamp', 'id'], True)



    
    @property
    def accounts_ledger(self):
        """All transactions broken down to sub account. Useful for looking at all journal entries in order for specific accounts.

        Returns:
            DataFrame: DataFrame with index ['account', 'sub_account', 'timestamp', 'type', 'symbol']
        """
        return self.set_ledger_index(
            ['account', 'sub_account', 'timestamp', 'type', 'symbol'])

    @property
    def positions_ledger(self):
        """ NOT CURRENTLY USING
        The most granular breakdown of transactions. Note, can be very long due to interest.

        Returns:
            DataFrame: DataFrame with index ['Account', 'Sub Account',  'Symbol', 'Timestamp', 'Position']
        """
        return self.set_ledger_index(
            ['account', 'sub_account', 'symbol', 'timestamp', 'position', "id"])

    @property
    def symbols(self):
        """All symbols contained in the transaction.

        Returns:
            list: A list containing the capitalized symbols.
        """
        return np.unique(np.array(self.ledger['symbol'].tolist()))

    @property
    def debit_value_sum(self):
        summary = self.summarize_ledger()
        return summary['debit_value'].sum()

    @property
    def debit_quantity_sum(self):
        summary = self.summarize_ledger()
        return summary['debit_quantity'].sum()
    
    @property
    def credit_value_sum(self):
        summary = self.summarize_ledger()
        return summary['credit_value'].sum()
    
    @property
    def credit_quantity_sum(self):
        summary = self.summarize_ledger()
        return summary['credit_quantity'].sum()
    
    def add_entry(self, entry):
        entry["incomplete"] = not is_row_valid(entry)
        self.entries.append(entry)

    def find_entries(self, query, regex=True):
        # Need to test
        if regex:
            return self.positions_ledger.filter(regex=query, axis=0)
        return self.positions_ledger.filter(like=query, axis=0)

    def set_ledger_index(self, index=['timestamp', 'id'], fill=False):
        ledger = self.raw_ledger
        if fill:
            ledger.fillna(0, inplace=True)
        ledger = self.raw_ledger.set_index(index)
        return ledger.sort_index()

    def summarize_ledger(self, index=['account', 'sub_account']):
        ledger = self.set_ledger_index(index, fill=True)
        regex = '(-\w+)'
        ledger = ledger.replace(value=0, regex=regex)
        ledger = ledger.groupby(level=[0,1]).sum(numeric_only=False)
        # Need to remove ugly columns here
        return ledger

    def merge(self, ledgers):
        for l in ledgers:
            for e in l.entries:
                self.add_entry(e)
