from datetime import datetime
import os
import logging
from tests.factories import TxnFactory
import pandas as pd
from randomtimestamp.functions import randomtimestamp

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

start = datetime.now()

# initialize bookkeeper
bk = BookKeeper()
bk.add_txs(txs, auto_detect=True)

eq_curve = bk.ledger.generate_equity_curve('assets')

# print(eq_curve)

print(datetime.now() - start)


# testing and creating ledger orientations below, please do not change.
# ^^ sorry mf i changed it 
# anyways, the ledger and entries are FINALLY working correctly! below gets the balances over time for each symbol (not filled)
# all_symbols = bk.ledger.symbols
# raw_timestamp_ledger = bk.ledger.simple
# raw_symbol_ledger = bk.ledger.apply_index(raw_timestamp_ledger, index=['symbol'])
# raw_symbol_ledger = bk.ledger.add_running_total(raw_symbol_ledger, 'assets')
# raw_symbol_assets_ledger = bk.ledger.apply_index(raw_symbol_ledger, index=['symbol', 'timestamp', 'type', 'id'])



# assets_simple = raw_timestamp_ledger

# raw_symbol_equities_ledger = bk.ledger.add_running_total(raw_symbol_assets_ledger)
# assets_running_qty = raw_symbol_equities_ledger.loc[raw_symbol_equities_ledger['debit_balance_quantity']>0]

# print(raw_symbol_assets_ledger)
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



# equities_simple = bk.ledger.apply_index(equities_simple, ['account_type'])
# raw_running_total = bk.ledger.add_running_total(equities_simple)
# raw_running_total_cron = bk.ledger.apply_index(raw_running_total)

# print(acct_symbol_ledger)
# print(raw_running_total_cron)




# def get_account_ledger(ledger, acct, sub_account):
#     # broke if indexed by account
#     return bk.ledger.accounts.loc[acct, sub_account]



# unrealized_gains_ledger = get_account_ledger(clean_ledger, 'assets', 'revenues', 'unrealized_gains_losses')
# crypto_ledger = get_account_ledger(clean_ledger, 'assets', 'current_assets', 'cryptocurrencies')
# cash_ledger = get_account_ledger(clean_ledger, 'current_assets', 'cash')

# print(bk.ledger.apply_index(['account','sub_account','symbol','timestamp', 'id'])[['debit_value', 'credit_value', 'debit_quantity', 'credit_quantity']].sum()

"""
PROPOSED CHANGES/IMPROVEMENTS

############ Legend ###############
## (C) Change | (I) Improvement  ##
###################################

(C) ENTRIES - remove "credit" & "debit" predicates from quantity and value keys, just rely on "side" when summarizing
(I) TX ENTRY SET - allow bookkeeper to run trial balance on a txs provided entry set before adding to ledger. This will help enforce the entry interface

Questions
1. Are expenses and liabilities both equities?
"""