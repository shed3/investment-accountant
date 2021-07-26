"""This module is for accounts and contains the base functions that control their balances and entries.

An account represents a single account for tracking transactions. Transactions may affect one or multiple accounts. 

  Typical usage example:

    cash = Acct(('Assets', 'Cash'), 'Asset', 'USD') 
    cash.inc(125.99, 125.99, 'Sell, 'Coinbase', datetime.datetime.now()) 
    cash.dec(40, 40, 'Buy, 'Coinbase', datetime.datetime.now()) 
"""

import logging
import pandas as pd
import numpy as np

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

        self.credits = []
        self.debits = []
        self.processed = False

    @property
    def raw_ledger(self):
        if len(self.debits) > 0 and len(self.credits) > 0:
            df = pd.merge(self.credits_df, self.debits_df, 'outer')
            return df.fillna(0)
        elif len(self.debits) > 0:
            return self.debits_df
        elif len(self.credits) > 0:
            return self.credits_df

    @property
    def ledger(self):
        """All transactions grouped by timestamp, type, and symbol. Useful for looking at all journal entries in order. Base ledger for every other operation.

        Returns:
            DataFrame: DataFrame with index ['Timestamp', 'ID']
        """
        if self.processed:
            return self.set_ledger_index()
        else:
            return pd.DataFrame(self.raw_ledger)

    @property
    def accounts_ledger(self):
        """All transactions broken down to sub account. Useful for looking at all journal entries in order for specific accounts.

        Returns:
            DataFrame: DataFrame with index ['Account', 'Sub Account', 'Timestamp', 'Type', 'Symbol']
        """
        return self.set_ledger_index(
            ['Account', 'Sub Account', 'Timestamp', 'Type', 'Symbol'])

    @property
    def positions_ledger(self):
        """The most granular breakdown of transactions. Note, can be very long due to interest.

        Returns:
            DataFrame: DataFrame with index ['Account', 'Sub Account', 'Connection ID',  'Symbol', 'Timestamp', 'Position']
        """
        return self.set_ledger_index(
            ['Account', 'Sub Account', 'Connection ID',  'Symbol', 'Timestamp', 'Position', "ID"])

    @property
    def symbols(self):
        """All symbols contained in the transaction.

        Returns:
            list: A list containing the capitalized symbols.
        """
        return np.unique(np.array(self.ledger['Symbol'].tolist()))

    @property
    def debits_df(self):
        return pd.DataFrame(self.debits).rename(columns={'Value': 'Debits', 'Quantity': 'Debits - Quantity'})

    @property
    def credits_df(self):
        return pd.DataFrame(self.credits).rename(columns={'Value': 'Credits', 'Quantity': 'Credits - Quantity'})

    def debit(self, **kwargs):
        # trans = {**kwargs}
        self.debits.append(kwargs)

    def credit(self, kwargs):
        trans = {**kwargs}
        self.credits.append(trans)

    def find_entries(self, query):
        # Need to test
        return self.positions_ledger.filter(like=query, axis=0)

    def set_ledger_index(self, index=['Timestamp', 'ID']):
        ledger = self.raw_ledger.set_index(index)
        return ledger.sort_index()

    def summarize_ledger(self, index=['Account', 'Sub Account']):
        ledger = self.set_ledger_index(index)
        ledger = ledger.sort_index()
        ledger = ledger.groupby(index).sum(numeric_only=True)
        return ledger

    def merge(self, ledgers):
        for ledger in ledgers:
            self.credits.append(ledger['credits'])
            self.debits.append(ledger['debits'])
