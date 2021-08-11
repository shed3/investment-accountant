import os
import logging

from randomtimestamp.functions import randomtimestamp
import pandas as pd

from src.crypto_accountant.bookkeeper import BookKeeper
from tests.fixtures import Fixes
from tests.factories import TxnFactory

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

pd.set_option("display.expand_frame_repr", False)
pd.set_option("display.width", 0)
pd.set_option('display.float_format', lambda x: '%.8f' % x)
pd.set_option("max_colwidth", 20)
pd.set_option("display.max_columns", 8)

firestore_cred_file = Fixes.firestore_cred_file(Fixes.storage_dir())

firestore_ref = Fixes.firestore_ref(firestore_cred_file)
# txs = Fixes.test_simple_swap()
# txs = Fixes.test_buy_sell_sequence()
# txs = Fixes.test_simple_buy_sell()
# txs = Fixes.test_sequence(0)
firebase_trans = Fixes.firestore_test_transactions(firestore_ref)
bk = BookKeeper()
# bk.add_txs(TxnFactory.hardcoded_txs())
# bk.add_txs(txs.transactions)
bk.add_txs(firebase_trans)

# print(bk.ledger.apply_index(['account','sub_account','symbol','timestamp']))
# print(bk.ledger.apply_index(['account','sub_account','symbol','timestamp', 'id'])[['debit_value', 'credit_value', 'debit_quantity', 'credit_quantity']].sum())

general_ledger = bk.ledger.raw
# print(general_ledger)


# print(bk.ledger.apply_index(['timestamp', 'type', 'symbol']))
# print(bk.ledger.summarize())
print(bk.ledger.raw.columns)
summary = bk.ledger.summarize(index=['account','sub_account','symbol'])
summary['balance'] = summary['debit_value'] - summary['credit_value']
print(bk.ledger.accounts.loc['revenues', 'realized_gains_losses'])
print(bk.ledger.accounts.filter(like='BCH', axis=0))


# print(bk.ledger.apply_index(['account','sub_account','symbol','timestamp', 'id'])[['debit_value', 'credit_value']].sum())
