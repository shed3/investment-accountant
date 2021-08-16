from datetime import datetime
import os
import logging
import numpy as np

from pandas.core.frame import DataFrame
from tests.factories import TxnFactory
import pandas as pd
from randomtimestamp.functions import randomtimestamp
import pystore
from decimal import Decimal
from src.crypto_accountant.bookkeeper import BookKeeper
from tests.fixtures import Fixes

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

pd.set_option("display.expand_frame_repr", False)
pd.set_option("display.width", 0)
pd.set_option('display.float_format', lambda x: '%.8f' % x)
pd.set_option("display.max_colwidth", 20)
pd.set_option("display.max_rows", None)
pd.set_option("display.min_rows", 100)
pd.set_option("display.max_columns", 8)

# Hardcoded transactions
# txs = TxnFactory.hardcoded_txs()

# Firebase Transactions
firestore_cred_file = Fixes.firestore_cred_file(Fixes.storage_dir())
firestore_ref = Fixes.firestore_ref(firestore_cred_file)
txs = Fixes.firestore_user_transactions(firestore_ref)

# Pystore historical data
pystore.set_path("/Volumes/CAPA/.storage")
store = pystore.store("messari")
historical_prices = store.collection('price')

def get_historical_df(symbols):
    df = pd.DataFrame()
    available_assets = historical_prices.list_items()
    not_found_assets = []
    for symbol in symbols:
        if symbol in available_assets:
            prices = historical_prices.item(symbol).to_pandas()
            prices[symbol] = prices['close'].apply(lambda x: Decimal(x))
            prices = prices.drop(['open', 'close', 'high', 'low', 'volume'], axis=1)
            if df.empty:
                df = prices.copy()
            else:
                df = df.join(prices, how='outer')
        else:
            not_found_assets.append(symbol)
    print(not_found_assets)
    df[not_found_assets] = np.nan   # create nan columns for unfound assets
    df['USD'] = Decimal(1)   # create nan columns for unfound assets
    df = df.fillna(Decimal(0))
    df.index = df.index.tz_localize(tz='UTC').floor('1D')
    return df


start = datetime.now()

# initialize bookkeeper
bk = BookKeeper()
bk.add_txs(txs, auto_detect=True)
# historical = get_historical_df(bk.ledger.symbols)
eq_curve = bk.ledger.generate_equity_curve('assets')

# multiply qty df with price df and then sum them all into total
# val_curve = eq_curve.mul(historical)
# val_curve['total'] = val_curve[bk.ledger.symbols].sum(axis=1)
# print(val_curve['total'])
print(eq_curve)
print(datetime.now() - start)


# (kaynes stuff) testing and creating ledger orientations below, please do not change.
# all_symbols = bk.ledger.symbols
# raw_timestamp_ledger = bk.ledger.simple
# equities_simple = raw_timestamp_ledger.loc[bk.ledger.simple['account_type']=='assets']
# raw_symbol_ledger = bk.ledger.apply_index(raw_timestamp_ledger, index=['symbol'])
# raw_symbol_equities_ledger = bk.ledger.apply_index(equities_simple, index=['symbol', 'id'])
# raw_symbol_ledger = bk.ledger.add_running_total(raw_symbol_ledger)
# raw_symbol_equities_ledger = bk.ledger.add_running_total(raw_symbol_equities_ledger)
# print(raw_symbol_equities_ledger)
# year_ledgers = [
#     # This can be done in a resample easier.
#     raw_timestamp_ledger['2017-01-01' :'2017-12-31'], 
#     raw_timestamp_ledger['2018-01-01' :'2018-12-31'], 
#     raw_timestamp_ledger['2019-01-01' :'2019-12-31'], 
#     raw_timestamp_ledger['2020-01-01' :'2020-12-31'], 
#     raw_timestamp_ledger['2021-01-01' :'2021-12-31']
# ]
# for year in year_ledgers:

#     acct_symbol_ledger = bk.ledger.apply_index(year, ['account_type', 'account','sub_account', 'symbol'], fill=True)
#     acct_symbol_ledger = bk.ledger.add_running_total(acct_symbol_ledger)
#     acct_symbol_summary = bk.ledger.summarize(acct_symbol_ledger)
#     print(acct_symbol_summary)


# acct_ledger = bk.ledger.accounts
# type_symbol_ledger = bk.ledger.apply_index(raw_timestamp_ledger, ['timestamp', 'type', 'symbol'])


"""
PROPOSED CHANGES/IMPROVEMENTS

############ Legend ###############
## (C) Change | (I) Improvement  ##
###################################

DONE | (C) ENTRIES - remove "credit" & "debit" predicates from quantity and value keys, just rely on "side" when summarizing
NOT DONT | (I) TX ENTRY SET - allow bookkeeper to run trial balance on a txs provided entry set before adding to ledger. This will help enforce the entry interface

Questions
1. Are expenses and liabilities both equities?
"""