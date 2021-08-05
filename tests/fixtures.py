import json
import os
from decimal import Decimal
from datetime import datetime
import random
from randomtimestamp.functions import randomtimestamp
from .factories import txn_factory

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
        txs.append(txn_factory('deposit', baseCurrency='usd'))
        txs.append(txn_factory('deposit', baseCurrency='btc'))
        txs.append(txn_factory('buy', baseCurrency='btc'))
        txs.append(txn_factory('receive', baseCurrency='btc'))
        txs.append(txn_factory('reward', baseCurrency='btc'))
        txs.append(txn_factory('interest-in-account', baseCurrency='btc'))
        txs.append(txn_factory('interest-in-stake', baseCurrency='btc'))
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
        txs.append(txn_factory('buy', baseCurrency='btc', timestamp=long_buy_date, baseUsdPrice=low_buy_price))
        txs.append(txn_factory('buy', baseCurrency='btc', timestamp=short_buy_date, baseUsdPrice=high_buy_price))
        txs.append(txn_factory('sell', baseCurrency='btc', quoteCurrency='usd', timestamp=sell_date, baseUsdPrice=high_sell_price))
        txs.append(txn_factory('sell', baseCurrency='btc', quoteCurrency='usd', timestamp=sell_date, baseUsdPrice=low_sell_price))
        txs.append(txn_factory('send', baseCurrency='btc', quoteCurrency='usd', timestamp=sell_date, baseUsdPrice=random_sell_price))
        return txs
    

    def test_sequence():
        return Fixes.test_deposit_buy() + Fixes.test_buy_sell_sequence()

