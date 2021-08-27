from datetime import datetime
import os
import logging
from tests.factories import TxnFactory
import numpy as np
import pandas as pd
import pystore
from decimal import Decimal
from tests.fixtures import Fixes
from src.crypto_accountant.bookkeeper import BookKeeper

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger(__name__)


pd.set_option("display.expand_frame_repr", False)
pd.set_option("display.width", 0)
pd.set_option('display.float_format', lambda x: '%.8f' % x)
pd.set_option("display.max_colwidth", 15)
pd.set_option("display.max_rows", None)
pd.set_option("display.min_rows", 100)
pd.set_option("display.max_columns", 8)

# Hardcoded transactions
txs = TxnFactory.hardcoded_txs()
# --- get symbols from hardcodes tx ---
symbols = ["BTC", "ETH"]

# # # Firebase Transactions
# firestore_cred_file = Fixes.firestore_cred_file(Fixes.storage_dir())
# firestore_ref = Fixes.firestore_ref(firestore_cred_file)
# txs = Fixes.firestore_user_transactions(firestore_ref)
# # --- get symbols from firebase tx ---
# base_symbols = list([x['baseCurrency'] for x in txs])
# quote_symbols = list([x['quoteCurrency'] for x in txs if "quoteCurrency" in x.keys()])
# symbols = set(base_symbols+quote_symbols)

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
    return df


def get_change_df(historical_df):
    return historical_df.diff()


start = datetime.now()



historical = get_historical_df(symbols)
log.info("Loaded historical data")
# initialize bookkeeper
bk = BookKeeper()
bk.add_historical_data(historical)
bk.add_txs(txs, auto_detect=False)

# eq_curve = bk.ledger.generate_equity_curve(['account_type', 'symbol'], 'balance_quantity')['assets']
# print('###########EQUITY CURVE##############')
# print(eq_curve)

journals = bk.ledger.all_account_journals
btc_balances_timeseries = bk.ledger.account_balances_timeseries['assets', 'current_assets', 'adj_fair_value', 'BTC']
balances_timeseries = bk.ledger.account_balances_timeseries
balances = bk.ledger.account_balances
btc_balances = balances['BTC']
print('###########ACCOUNT JOURNALS##############')
# print(bk.ledger.simple)
print(journals)
# print(len(journals))
print(balances_timeseries)
print(balances)
# print(btc_balances)


# multiply qty df with price df and then sum them all into total

# val_curve = eq_curve.mul(historical)
# val_curve['total'] = val_curve[bk.ledger.symbols].sum(axis=1)
# print(val_curve['total'])
# print(datetime.now() - start)


# TODO
"""
Account Journals - Index ['account_type', 'account', 'sub_account', 'timestamp'] - symbol?
    Post Account Journal Balances to General Ledger at each transaction, maybe every day, could only save changes and ffill
Trial Balance

Adjusting Entries:
    Accrue Receivables / Payables
    Adjust to Fair Value
    Post to General Journal
General Journal - All adjusting entries, same index as account journals.
Post general journal account balances to general ledger
General Ledger - Indexed the same, but only has one entry per timestamp (summarized)
Adjusted Trial Balance
"""
