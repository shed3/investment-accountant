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


# Firebase Transactions
firestore_cred_file = Fixes.firestore_cred_file(Fixes.storage_dir())
firestore_ref = Fixes.firestore_ref(firestore_cred_file)
txs = Fixes.firestore_user_transactions(firestore_ref)

# Hardcoded transactions
# txs = TxnFactory.hardcoded_txs()

# initialize bookkeeper
bk = BookKeeper()
bk.add_txs(txs, auto_detect=True)




# testing and creating ledger orientations below, please do not change.
all_symbols = bk.ledger.symbols
raw_timestamp_ledger = bk.ledger.simple
equities_simple = raw_timestamp_ledger.loc[bk.ledger.simple['account_type']=='assets']
raw_symbol_ledger = bk.ledger.apply_index(raw_timestamp_ledger, index=['symbol'])
raw_symbol_equities_ledger = bk.ledger.apply_index(equities_simple, index=['symbol', 'id'])
raw_symbol_ledger = bk.ledger.add_running_total(raw_symbol_ledger)
raw_symbol_equities_ledger = bk.ledger.add_running_total(raw_symbol_equities_ledger)
print(raw_symbol_equities_ledger)
year_ledgers = [
    # This can be done in a resample easier.
    raw_timestamp_ledger['2017-01-01' :'2017-12-31'], 
    raw_timestamp_ledger['2018-01-01' :'2018-12-31'], 
    raw_timestamp_ledger['2019-01-01' :'2019-12-31'], 
    raw_timestamp_ledger['2020-01-01' :'2020-12-31'], 
    raw_timestamp_ledger['2021-01-01' :'2021-12-31']
]
for year in year_ledgers:

    acct_symbol_ledger = bk.ledger.apply_index(year, ['account_type', 'account','sub_account', 'symbol'], fill=True)
    acct_symbol_ledger = bk.ledger.add_running_total(acct_symbol_ledger)
    acct_symbol_summary = bk.ledger.summarize(acct_symbol_ledger)
    print(acct_symbol_summary)


acct_ledger = bk.ledger.accounts
type_symbol_ledger = bk.ledger.apply_index(raw_timestamp_ledger, ['timestamp', 'type', 'symbol'])



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
