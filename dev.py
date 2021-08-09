import os
import logging
import pandas as pd

from src.crypto_accountant.transaction import Transaction
from src.crypto_accountant.bookkeeper import BookKeeper
from tests.fixtures import Fixes

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

# pandas config
pd.set_option("display.expand_frame_repr", False)
pd.set_option("display.width", 0)
pd.set_option('display.float_format', lambda x: '%.8f' % x)
pd.set_option("max_colwidth", 25)
pd.set_option("display.max_columns", 8)

txs = Fixes.test_new_buy_sell()
print(txs[1].get_affected_balances())
# txs = Fixes.test_simple_swap()
# txs = Fixes.test_buy_sell_sequence()
# txs = Fixes.test_simple_buy_sell()
bk = BookKeeper()
# bk.add_txs(txs)
# print(bk.ledger.apply_index(['account','sub_account','symbol','timestamp']))
# print(bk.ledger.apply_index(['account','sub_account','symbol','timestamp', 'id'])[['debit_value', 'credit_value', 'debit_quantity', 'credit_quantity']].sum())

"""
Start: Transactions (list)
Start: Current Ledger
Given: Transactions (list) - Accepts add and delete transactions, but not edit?
Given: Ledger (one or list)

Riley sends cleaned transactions, needs ledger, balances, timeseries w/ analysis
Riley sends current market data, needs updated ledger, balances.
Riley sends new transaction, needs added to ledger, return updated balances and timeseries
"""