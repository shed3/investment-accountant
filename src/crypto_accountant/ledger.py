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
from decimal import Decimal
from re import T
import pandas as pd
import numpy as np

class Ledger:

    def __init__(self) -> None:

        self.entries = []

    @property
    def raw(self):
        """


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
        All entries grouped by timestamp and id.
        Useful for ordering chronological. 

        Returns:
            DataFrame: DataFrame with index ['timestamp', 'id']
        """
        return self.apply_index(self.raw, fill=True)

    
    @property
    def all_account_journals(self):
        """
        All journal entries indexed down to sub account, symbol, timestamp. Used to derive account_balances for initial trial balance.

        Returns:
            DataFrame: DataFrame with index ['account_type', 'account', 'sub_account', 'symbol']
        """
        return self.apply_index(self.simple, 
            ['account_type', 'account', 'sub_account', 'symbol', 'timestamp'])

    @property
    def account_balances(self):
        """
        Summarized account_journals. Posted to general ledger with timestamp index. Used for trial balance before adjusting entries.

        Returns:
            DataFrame: DataFrame with index ['account_type', 'account', 'sub_account'] columns [symbols] value sum.
        """
        ledger = self.add_balance(self.all_account_journals)
        summary_symbol = (ledger
            .groupby(['account_type', 'account', 'sub_account', 'symbol'])['balance']
            .apply(lambda x: x.sum())
            .reset_index()
            .pivot(['account_type', 'account', 'sub_account'], 'symbol', 'balance')
        )
        return summary_symbol

    @property
    def account_balances_timeseries(self):
        """
        Summarized account_journals. Posted to general ledger with timestamp index. Used for trial balance before adjusting entries.

        Returns:
            DataFrame: DataFrame with index ['account_type', 'account', 'sub_account'] columns [symbols] value sum.
        """
        ledger = self.add_balance(self.all_account_journals)
        timeseries_summary = (ledger
            .groupby(['account_type', 'account', 'sub_account', 'symbol', 'timestamp'])['balance']
            .apply(lambda x: x.sum())
            .reset_index()
            .pivot('timestamp', ['account_type', 'account', 'sub_account', 'symbol'], 'balance')                
            .fillna(Decimal(0))
            .cumsum()
        )
        return timeseries_summary

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

    def generate_equity_curve(self, group_by, value_column):
        # calculate debit and credit qty balanaces for given account type

        # ledger = self.simple.copy()
        ledger = self.add_balance(self.all_account_journals)
        # ledger['account_type_quantity'] = ledger['quantity'].where((ledger['account_type'] == account_type), 0)
        # ledger['debit_balance'] = ledger['account_type_quantity'].where(ledger['side'] == 'debit', 0)
        # ledger['credit_balance'] = ledger['account_type_quantity'].where(ledger['side'] == 'credit', 0)

        # # calculate balance according to account type
        # if account_type == 'assets':
        #     ledger['balance'] = ledger['debit_balance'] - ledger['credit_balance']
        # else:
        #     ledger['balance'] =  ledger['credit_balance'] - ledger['debit_balance']
        
        # create new df with timestamp (index), symbol, and balance
        # convert timestamps to utc then round down to nearest day

        # affected_symbol_balances = ledger[['symbol', 'balance_quantity']].copy()

        #! DO NOT MESS WITH THE ORDER BELOW
        # Affected Symbol Balances -> Equity Curve
        # 1. group df by timestamp and symbol
        # 2. sum balances to get symbols' affected balances each day
        # 3. reset index to place timestamp back in columns
        # 3. pivote with index=timestamp, columns=symbol, values=balance
        #      this restructures df
        #      from -> timestamp | symbol | balance |
        #      to   -> timestamp | symbols[0] | ... | symbols[n]
        #      where the values in symbols[n] represent that symbols total affected balance that day
        # 4. remove colunm name "symbol", set to None
        # 5. Expand df to include row for everyday between first and last entry
        # 6. Set unavailable balances to 0
        # 6. Run cumsum on all symbol columns to get running balances
        # ledger = (
        #     ledger
        #         .reset_index()
        #         .set_index('timestamp')
        #         .tz_convert(tz='UTC')
        #         # .index.get_level_values(-1).floor('1D')
        # )
        ledger.reset_index(inplace=True)
        ledger.set_index('timestamp', inplace=True)
        ledger.index = ledger.index.tz_convert(tz='UTC').floor('1D')

        eq_curve = (
            ledger
                .reset_index()
                .groupby([*group_by, 'timestamp'])[value_column]
                .apply(lambda x: x.sum())
                .reset_index()
                .pivot('timestamp', group_by, value_column)
                .asfreq(freq='1D', normalize=True)
                .fillna(Decimal(0))
                .cumsum()
        )
        return eq_curve

    # def generate_equity_curve(self, account_type):
    #     # calculate debit and credit qty balanaces for given account type

    #     ledger = self.simple.copy()
    #     ledger['account_type_quantity'] = ledger['quantity'].where((ledger['account_type'] == account_type), 0)
    #     ledger['debit_balance'] = ledger['account_type_quantity'].where(ledger['side'] == 'debit', 0)
    #     ledger['credit_balance'] = ledger['account_type_quantity'].where(ledger['side'] == 'credit', 0)

    #     # calculate balance according to account type
    #     if account_type == 'assets':
    #         ledger['balance'] = ledger['debit_balance'] - ledger['credit_balance']
    #     else:
    #         ledger['balance'] =  ledger['credit_balance'] - ledger['debit_balance']
        
    #     # create new df with timestamp (index), symbol, and balance
    #     # convert timestamps to utc then round down to nearest day
    #     affected_symbol_balances = ledger[['symbol', 'balance']].copy()
    #     affected_symbol_balances.index = affected_symbol_balances.index.tz_convert(tz='UTC').floor('1D')

    #     #! DO NOT MESS WITH THE ORDER BELOW
    #     # Affected Symbol Balances -> Equity Curve
    #     # 1. group df by timestamp and symbol
    #     # 2. sum balances to get symbols' affected balances each day
    #     # 3. reset index to place timestamp back in columns
    #     # 3. pivote with index=timestamp, columns=symbol, values=balance
    #     #      this restructures df
    #     #      from -> timestamp | symbol | balance |
    #     #      to   -> timestamp | symbols[0] | ... | symbols[n]
    #     #      where the values in symbols[n] represent that symbols total affected balance that day
    #     # 4. remove colunm name "symbol", set to None
    #     # 5. Expand df to include row for everyday between first and last entry
    #     # 6. Set unavailable balances to 0
    #     # 6. Run cumsum on all symbol columns to get running balances
    #     eq_curve = (
    #         affected_symbol_balances
    #             .groupby(['timestamp','symbol'])['balance']
    #             .apply(lambda x: x.sum())
    #             .reset_index()
    #             .pivot('timestamp', 'symbol', 'balance')
    #             .rename_axis(columns=None)
    #             .asfreq(freq='1D', normalize=True)
    #             .fillna(Decimal(0))
    #             .cumsum()
    #     )
    #     return eq_curve

    def add_balance(self, ledger):
        ledger['debit_quantity'] = ledger['quantity'].where(ledger['side'] == 'debit' , 0)
        ledger['debit_value'] = ledger['value'].where(ledger['side'] == 'debit' , 0)

        ledger['credit_quantity'] = ledger['quantity'].where(ledger['side'] == 'credit', 0)
        ledger['credit_value'] = ledger['value'].where(ledger['side'] == 'credit', 0)

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

    def add_running_total(self, ledger, account_type):
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


"""
Ledger
    get_account_journals(index) - account_type, account, sub_account
    get_account_balance(index, timestamp=none) - account_type, account, sub_account if timestamp, filter all transactions after timestamp
    get_account_balance_timeseries(index, normalized=True, column=balance_quantity) - account_type, account, sub_account. normalized determines whether to have regular intervals.

"""
                
