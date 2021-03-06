from datetime import datetime
import os
import logging
import numpy as np
import pandas as pd
import pystore
from decimal import Decimal
from tests.fixtures import Fixes
from src.crypto_accountant.bookkeeper import BookKeeper

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
eq_curve = bk.ledger.generate_equity_curve('assets')
print(eq_curve)

# multiply qty df with price df and then sum them all into total
# historical = get_historical_df(bk.ledger.symbols)
# val_curve = eq_curve.mul(historical)
# val_curve['total'] = val_curve[bk.ledger.symbols].sum(axis=1)
# print(val_curve['total'])
print(datetime.now() - start)
