import json
import os
from decimal import Decimal
from datetime import datetime, timedelta
import random
import pandas as pd
import pytz
import uuid

import firebase_admin
from firebase_admin import credentials, firestore
from .factories import TxnFactory
from src.crypto_accountant.transactions.buy import Buy
from src.crypto_accountant.transactions.sell import Sell
from src.crypto_accountant.transactions.swap import Swap

from .utils import generate_timestamp


class Fixes:
    def storage_dir():
        return '/Volumes/CAPA/.storage/'

    def firestore_cred_file(storage_dir):
        return storage_dir + \
            "creds/shed-enterprises-firebase-adminsdk-coq5l-514bd580bf.json"

    def firestore_ref(firestore_cred_file):
        if not firebase_admin._apps:
            cred = credentials.Certificate(firestore_cred_file)
            firebase_admin.initialize_app(cred)
        return firestore.client()

    def firestore_test_transactions(firestore_ref):
        trans_ref = firestore_ref.collection(u'transactions')
        raw_transactions = trans_ref.get()
        all_transactions = []
        for raw in raw_transactions:
            trans = raw.to_dict()
            all_transactions.append(trans)
        return sorted(all_transactions, key=lambda x: x['timestamp'])

    def firestore_user_transactions(firestore_ref, uid='903Rf3cVflW2bzWc8x1YL8E78gy1'):
        trans_ref = firestore_ref.collection(u'transactions')
        riley_trans = trans_ref.where(u'uid', u'==', u'903Rf3cVflW2bzWc8x1YL8E78gy1')
        raw_transactions = riley_trans.get()
        all_transactions = []
        for raw in raw_transactions:
            trans = raw.to_dict()
            all_transactions.append(trans)
        return sorted(all_transactions, key=lambda x: x['timestamp'])

    def local_txs(file_path=''):
        file = file_path if file_path else os.path.dirname(os.path.realpath(__file__)) + "/example_txs.json"
        with open(file, 'r') as json_file:
            all_trans = json.load(json_file)
            for trans in all_trans:
                for key in trans:
                    val = trans[key]
                    if isinstance(val, int) or isinstance(val, float):
                        val = Decimal(str(val))
                    trans[key] = val
        return sorted(all_trans, key=lambda x: x['timestamp'])

    def test_simple_buy_sell():
        short_buy_date = generate_timestamp(start_year=pd.Timestamp.now().year)
        long_buy_date = generate_timestamp(start_year=2018)
        sell_date = generate_timestamp(start=short_buy_date)
        factory = TxnFactory()
        buy = factory.generic_factory('buy', base_currency='btc', quote_currency='usd', timestamp=long_buy_date,
                                      base_usd_price=1000, quote_usd_price=1, base_quantity=1, quote_quantity=1000, fee_quantity=0)
        sell = factory.generic_factory('sell', base_currency='btc', quote_currency='usd', timestamp=sell_date,
                                       base_usd_price=2000, quote_usd_price=1, quote_quantity=1000, taxable=True, base_quantity=.5, fee_quantity=0)
        return [
            buy,
            sell,
        ]

    def test_new_buy_sell():
        short_buy_date = generate_timestamp(start_year=pd.Timestamp.now().year)
        long_buy_date = generate_timestamp(start_year=2018)
        sell_date = generate_timestamp(start=short_buy_date)
        buy = TxnFactory.txn_factory('buy', base_currency='btc', quote_currency='usd', timestamp=long_buy_date,
                                     base_usd_price=1000, quote_usd_price=1, base_quantity=1, quote_quantity=1000, fee_quantity=5)
        sell = TxnFactory.txn_factory('sell', base_currency='btc', quote_currency='usd', timestamp=sell_date, base_usd_price=2000,
                                      quote_usd_price=1, quote_quantity=1000, taxable=True, base_quantity=.5, fee_quantity=.005, fee_currency='btc', fee_usd_price=2000)

        return [
            Buy(**buy.to_dict),
            Sell(**sell.to_dict),
        ]

    def test_simple_swap():
        short_buy_date = generate_timestamp(start_year=pd.Timestamp.now().year)
        long_buy_date = generate_timestamp(start_year=2018)
        sell_date = generate_timestamp(start=short_buy_date)
        factory = TxnFactory()
        buy = factory.generic_factory('buy', base_currency='btc', quote_currency='usd', timestamp=long_buy_date,
                                      base_usd_price=1000, quote_usd_price=1, base_quantity=1, quote_quantity=1000, fee_quantity=.01)
        swap = factory.generic_factory('swap', base_currency='eth', quote_currency='btc', timestamp=sell_date,
                                       base_usd_price=2000, quote_usd_price=10000, base_quantity=1, quote_quantity=.2, fee_quantity=.01, taxable=True)
        return [
            buy,
            swap,
        ]
        # return [
        #     Buy(**buy),
        #     Swap(**swap),
        # ]

    def test_sequence(qty=10):
        factory = TxnFactory()
        factory.deposit_factory()
        factory.deposit_factory()
        factory.deposit_factory()
        factory.deposit_factory()
        factory.buy_factory()
        factory.buy_factory()
        factory.buy_factory()
        factory.sell_factory()
        factories = [factory.deposit_factory, factory.buy_factory, factory.sell_factory, factory.receive_factory]
        for x in range(qty):
            tx = factories[random.randint(0, len(factories)-1)]
            tx()
        # factory.swap_factory()
        return factory


'''
deposit - no rules
withdrawal - not more than balance
buy - not more usd than balance
sell - not more asset than balance
send - not more asset than balance
swap - not more than quote asset balance
receive ish - no rules

'''

# deposit USD (5,000)
# receive USDC (5,000)
# receive BTC (1) (price 1000)
# (buy / sell /swap) (gain / loss) (short / long term) (single / multi close)
# buy, sell gain (short term) (single position)
# buy, sell gain (short term) (multi position)
# buy, sell gain (long term)
# buy, sell loss (short term)
# buy, sell loss (long term)
# send, gain
# send, loss
# swap, gain
# swap, loss
# fee, gain
# fee, loss
