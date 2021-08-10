import json
import os
from decimal import Decimal
from datetime import datetime
import random
from randomtimestamp.functions import randomtimestamp
from .factories import txn_factory
from src.crypto_accountant.transactions.buy import Buy
from src.crypto_accountant.transactions.sell import Sell
from src.crypto_accountant.transactions.swap import Swap

class Fixes:

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

    def generate_test_txns(num_txs_per_type=1, symbols=['btc', 'eth', 'grt']):
        tx_types = ['deposit', 'receive', 'buy', 'reward', 'interest-in-account', 'interest-in-stake','sell', 'withdrawal', 'send']
        txs = []
        for x in range(num_txs_per_type):
            txs += list([txn_factory(tx_type) for tx_type in tx_types])
        return txs

    def test_deposit_buy():
        txs = []
        txs.append(txn_factory('deposit', base_currency='usd'))
        txs.append(txn_factory('deposit', base_currency='btc'))
        txs.append(txn_factory('buy', base_currency='btc'))
        txs.append(txn_factory('receive', base_currency='btc'))
        txs.append(txn_factory('reward', base_currency='btc'))
        txs.append(txn_factory('interest-in-account', base_currency='btc'))
        txs.append(txn_factory('interest-in-stake', base_currency='btc'))
        return txs


    def test_buy_sell_sequence():
        txs = []
        short_buy_date = randomtimestamp(start_year=datetime.now().year, text=False)
        long_buy_date = randomtimestamp(start_year=2018, text=False)
        low_buy_price = random.randint(30, 50)
        high_buy_price = random.randint(50, 70)
        low_sell_price = random.randint(0, 30)
        high_sell_price = random.randint(70, 100)
        random_sell_price = random.randint(0, 100)
        sell_date = randomtimestamp(start=short_buy_date, text=False)
        txs.append(txn_factory('buy', base_currency='btc', timestamp=long_buy_date, base_usd_price=low_buy_price))
        txs.append(txn_factory('buy', base_currency='btc', timestamp=short_buy_date, base_usd_price=high_buy_price))
        txs.append(txn_factory('sell', base_currency='btc', quote_currency='usd', timestamp=sell_date, base_usd_price=high_sell_price, taxable=True))
        txs.append(txn_factory('sell', base_currency='btc', quote_currency='usd', timestamp=sell_date, base_usd_price=low_sell_price, taxable=True))
        txs.append(txn_factory('send', base_currency='btc', quote_currency='usd', timestamp=sell_date, base_usd_price=random_sell_price))
        return txs
    
    def test_simple_buy_sell():
        short_buy_date = randomtimestamp(start_year=datetime.now().year, text=False)
        long_buy_date = randomtimestamp(start_year=2018, text=False)
        sell_date = randomtimestamp(start=short_buy_date, text=False)
        txs = [
            txn_factory('buy', base_currency='btc', quote_currency='usd', timestamp=long_buy_date, base_usd_price=1000, quote_usd_price=1, base_quantity=1, quote_quantity=1000, fee_quantity=0),
            txn_factory('sell', base_currency='btc', quote_currency='usd', timestamp=sell_date, base_usd_price=2000, quote_usd_price=1, quote_quantity=1000, taxable=True, base_quantity=.5, fee_quantity=0)
        ]
        return txs

    def test_new_buy_sell():
        short_buy_date = randomtimestamp(start_year=datetime.now().year, text=False)
        long_buy_date = randomtimestamp(start_year=2018, text=False)
        sell_date = randomtimestamp(start=short_buy_date, text=False)
        buy = txn_factory('buy', base_currency='btc', quote_currency='usd', timestamp=long_buy_date, base_usd_price=1000, quote_usd_price=1, base_quantity=1, quote_quantity=1000, fee_quantity=5)
        sell = txn_factory('sell', base_currency='btc', quote_currency='usd', timestamp=sell_date, base_usd_price=2000, quote_usd_price=1, quote_quantity=1000, taxable=True, base_quantity=.5, fee_quantity=.005, fee_currency='btc', fee_usd_price=2000)

        return [
            Buy(**buy.to_dict),
            Sell(**sell.to_dict),
        ]
    
    def test_simple_swap():
        short_buy_date = randomtimestamp(start_year=datetime.now().year, text=False)
        long_buy_date = randomtimestamp(start_year=2018, text=False)
        sell_date = randomtimestamp(start=short_buy_date, text=False)

        buy = txn_factory('buy', base_currency='btc', quote_currency='usd', timestamp=long_buy_date, base_usd_price=1000, quote_usd_price=1, base_quantity=1, quote_quantity=1000, fee_quantity=.01)
        swap = txn_factory('swap', base_currency='eth', quote_currency='btc', timestamp=sell_date, base_usd_price=2000, quote_usd_price=10000, base_quantity=1, quote_quantity=.2, fee_quantity=.01, taxable=True)
        
        return [
            Buy(**buy.to_dict),
            Swap(**swap.to_dict),
        ]

    def test_sequence():
        return Fixes.test_buy_sell_sequence()

