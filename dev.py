import os
import logging

from randomtimestamp.functions import randomtimestamp
import pandas as pd

from src.crypto_accountant.bookkeeper import BookKeeper
from tests.fixtures import Fixes

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

pd.set_option("display.expand_frame_repr", False)
pd.set_option("display.width", 0)
pd.set_option('display.float_format', lambda x: '%.8f' % x)
pd.set_option("max_colwidth", 25)
pd.set_option("display.max_columns", 8)

# txs = Fixes.test_simple_swap()
# txs = Fixes.test_buy_sell_sequence()
# txs = Fixes.test_simple_buy_sell()
txs = Fixes.test_sequence()

bk = BookKeeper()
bk.add_txs(txs.transactions)

print(bk.ledger.apply_index(['account','sub_account','symbol','timestamp']))
for position in bk.positions.values():
    print(position.symbol, position.balance)
# print(bk.ledger.apply_index(['account','sub_account','symbol','timestamp', 'id'])[['debit_value', 'credit_value', 'debit_quantity', 'credit_quantity']].sum())

general_ledger = bk.ledger.raw
print(general_ledger)


# print(bk.ledger.apply_index(['timestamp', 'type', 'symbol']))
# print(bk.ledger.summarize())
print(bk.ledger.apply_index(['account','sub_account','symbol','timestamp', 'id'])[['debit_value', 'credit_value', 'debit_quantity', 'credit_quantity']].sum())
