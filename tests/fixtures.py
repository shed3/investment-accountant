import json
import os
from decimal import Decimal
from datetime import datetime
import random
from randomtimestamp.functions import randomtimestamp
from .factories import TxnFactory

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

    def test_simple_buy_sell():
        short_buy_date = randomtimestamp(start_year=datetime.now().year, text=False)
        long_buy_date = randomtimestamp(start_year=2018, text=False)
        sell_date = randomtimestamp(start=short_buy_date, text=False)
        txs = [
            TxnFactory.TxnFactory.txn_factory('buy', base_currency='btc', quote_currency='usd', timestamp=long_buy_date, base_usd_price=1000, quote_usd_price=1, base_quantity=1, quote_quantity=1000, fee_quantity=0),
            TxnFactory.txn_factory('sell', base_currency='btc', quote_currency='usd', timestamp=sell_date, base_usd_price=2000, quote_usd_price=1, quote_quantity=1000, taxable=True, base_quantity=.5, fee_quantity=0)
        ]
        return txs
    
    def test_simple_swap():
        short_buy_date = randomtimestamp(start_year=datetime.now().year, text=False)
        long_buy_date = randomtimestamp(start_year=2018, text=False)
        sell_date = randomtimestamp(start=short_buy_date, text=False)

        txs = [
            TxnFactory.txn_factory('buy', base_currency='btc', quote_currency='usd', timestamp=long_buy_date, base_usd_price=1000, quote_usd_price=1, base_quantity=1, quote_quantity=1000, fee_quantity=.01),
            TxnFactory.txn_factory('swap', base_currency='eth', quote_currency='btc', timestamp=sell_date, base_usd_price=2000, quote_usd_price=10000, base_quantity=1, quote_quantity=.2, fee_quantity=.01, taxable=True),
        ]
        return txs

    def test_sequence(qty=10):
        factory = TxnFactory()
        factory.deposit_factory()
        factory.buy_factory()
        factory.sell_factory()
        factories = [factory.deposit_factory, factory.buy_factory, factory.sell_factory, factory.receive_factory]
        for x in range(qty):
            tx = factories[random.randint(0, len(factories)-1)]
            tx()
        factory.swap_factory()
        factory.swap_factory()
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
