import os
import logging
import pandas as pd

from src.crypto_accountant.transaction import Transaction
from src.crypto_accountant.account import Account
from src.crypto_accountant.bookkeeper import BookKeeper
from tests.fixtures import Fixes

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

# pandas config
pd.set_option("display.expand_frame_repr", False)
pd.set_option("display.width", 0)
pd.set_option('display.float_format', lambda x: '%.8f' % x)
pd.set_option("max_colwidth", 60)
pd.set_option("display.max_columns", 10)

txs = Fixes.test_sequence()
bk = BookKeeper()
bk.add_txs(txs)
print(bk.accounts)

# acct = Account("Assets", "Inv", "Test")
# acct.add_txs(txs)
# print(acct.positions['btc'].unrealized_gain)


# print(bk.journal.find_entries('^(-\w+)'))
# print(bk.journal.ledger)
# print(bk.journal.ledger.reset_index()[['symbol', 'position','debit_value', 'credit_value', 'debit_quantity', 'credit_quantity', 'incomplete',]])






"""
Possible Flags
* position: -feePrice or -closePosition
* credit_value: -closeValue or -closeGain
* credit_quantity: -closeQuantity
* debit_value: -closeTotal
* debit_quantity : -closeQuoteQuantity

Start: Transactions (list)
Start: Current Ledger
Given: Transactions (list) - Accepts add and delete transactions, but not edit?
Given: Ledger (one or list)



Riley sends cleaned transactions, needs ledger, balances, timeseries w/ analysis
Riley sends current market data, needs updated ledger, balances.
Riley sends new transaction, needs added to ledger, return updated balances and timeseries


"""