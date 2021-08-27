import uuid
import pytz
import random
import pandas as pd
from datetime import datetime, timedelta
from src.crypto_accountant.utils import check_type
from src.crypto_accountant.position import Position
from src.crypto_accountant.transactions.buy import Buy
from src.crypto_accountant.transactions.sell import Sell
from src.crypto_accountant.transactions.swap import Swap
from src.crypto_accountant.transactions.deposit import Deposit
from src.crypto_accountant.transactions.withdrawal import Withdrawal
from src.crypto_accountant.transactions.send import Send
from src.crypto_accountant.transactions.receive import Receive

from .utils import generate_timestamp


class TxnFactory:
    def __init__(self):
        self.positions = {
            'USD': Position('USD'),
            'BTC': Position('BTC'),
            'ETH': Position('ETH'),
            # 'link': Position('link'),
            # # 'USDC': Position('USDC'),
            # 'grt': Position('grt'),
            # 'ada': Position('ada'),
        }
        self.data_factory = HistoricalDataFactory()
        self.date_range = self.data_factory.date_range
        self.eod_data = self.data_factory.data
        for symbol in self.positions.keys():
            self.positions[symbol].mkt_price = check_type(
                self.eod_data[symbol].iloc[0]['close'])
            self.positions[symbol].mkt_timestamp = check_type(
                self.eod_data[symbol].index[0])
        self.transactions = []

    def get_rand_currency(self, available_assets=[], excludes=[]):
        excludes.append('USD')
        if len(available_assets) == 0:
            available_assets = list(
                [x for x in self.positions.keys() if x not in excludes])
        return available_assets[random.randint(0, len(available_assets) - 1)]

    def generate_fee(self, qty, price=1, symbol='USD', max_pct_diff=7):
        fee = {}
        fee_total_q = qty * \
            check_type(random.randint(1, max_pct_diff)) * check_type(.01)
        fee['qty'] = fee_total_q
        fee['price'] = price
        fee['symbol'] = symbol
        return fee

    def generic_factory(self, tx_type, include_fee=False, **kwargs):
        args = {
            'type': tx_type,
            'id': kwargs.get("id", uuid.uuid4()),
            'timestamp': kwargs.get('timestamp', generate_timestamp(start_year=2018)),
            'base_currency': kwargs.get('base_currency', 'BTC'),
            'base_usd_price': kwargs.get('base_usd_price', check_type(random.randint(8000, 10000))),
            'base_quantity': kwargs.get('base_quantity', check_type(random.randint(1, 10)))
        }

        if 'quote_currency' in kwargs:
            args['quote_currency'] = kwargs['quote_currency']
            args['quote_usd_price'] = kwargs['quote_usd_price']
            args['quote_quantity'] = kwargs['quote_quantity']

        if include_fee:
            mkt = kwargs.get('mkt', 'base')
            fee = self.generate_fee(args['base_quantity'], args.get(
                '{}_usd_price'.format(mkt), 1), args.get('{}_currency'.format(mkt), 'BTC'))
            args['fee_quantity'] = fee['qty']
            args['fee_usd_price'] = fee['price']
            args['fee_currency'] = fee['symbol']

        return args

    def deposit_factory(self, base_quantity=check_type(random.randint(0, 10000)), include_fee=False, **kwargs):
        args = {
            'base_currency': 'USD',
            'base_usd_price': check_type(1),
            'base_quantity': base_quantity,
            'timestamp': kwargs.get("timestamp", generate_timestamp(start_year=2018))
        }
        tx_kwargs = self.generic_factory('deposit', include_fee=include_fee, **args)
        tx = Deposit(**tx_kwargs)
        self.positions['USD'].add(tx.id, check_type(
            1), tx.timestamp, tx.assets['base'].quantity)
        self.transactions.append(tx)

    def receive_factory(self, include_fee=False, **kwargs):
        base_currency = kwargs.get("base_currency", self.get_rand_currency())
        timestamp = kwargs.get("timestamp", generate_timestamp(start_year=2018))
        args = {
            'base_currency': base_currency,
            'base_usd_price': self.data_factory.get_price(base_currency, timestamp),
            'base_quantity': kwargs.get('base_quantity', check_type(random.randint(1, 100))),
            'timestamp': timestamp
        }
        tx_kwargs = self.generic_factory('receive', include_fee=include_fee, **args)
        tx = Receive(**tx_kwargs)
        self.positions[base_currency].add(
            tx.id, tx.assets['base'].usd_price, tx.timestamp, tx.assets['base'].quantity)
        self.transactions.append(tx)

    def buy_factory(self, **kwargs):
        base_currency = kwargs.get("base_currency", self.get_rand_currency())
        timestamp = generate_timestamp(
            start=self.positions['USD'].mkt_timestamp.tz_convert(tz=None))
        quote_quantity = check_type(
            random.uniform(.1, float(self.positions['USD'].balance)))
        base_usd_price = self.data_factory.get_price(base_currency, timestamp)
        base_quantity = quote_quantity / base_usd_price
        args = {
            'base_currency': base_currency,
            'base_usd_price': base_usd_price,
            'base_quantity': base_quantity,
            'timestamp': timestamp
        }
        include_fee = kwargs.get('include_fee', bool(random.randint(0, 1)))
        tx_kwargs = self.generic_factory('buy', include_fee=include_fee, **args)
        tx_kwargs['quote_currency'] = 'USD'
        tx_kwargs['quote_usd_price'] = check_type(1)
        tx_kwargs['quote_quantity'] = quote_quantity
        tx = Buy(**tx_kwargs)
        self.positions[base_currency].add(
            tx.id, tx.assets['base'].usd_price, tx.timestamp, tx.assets['base'].quantity)
        self.positions['USD']._closes[tx.id] = {
            'timestamp': tx.timestamp,
            'price': check_type(1),
            'qty': quote_quantity,
            'realized_gain': 0
        }
        self.positions['USD'].adjust_to_mtk(check_type(1), timestamp)
        self.transactions.append(tx)

    def swap_factory(self, **kwargs):
        available_assets = list([x.symbol for x in self.positions.values() if x.balance > 0])
        base_currency = kwargs.get("base_currency", self.get_rand_currency())
        quote_currency = kwargs.get("base_currency", self.get_rand_currency(available_assets, excludes=[base_currency]))
        quote_position = self.positions[quote_currency]
        timestamp = kwargs.get("timestamp", generate_timestamp(
            start=quote_position.mkt_timestamp.tz_convert(tz=None)))
        quote_usd_price = self.data_factory.get_price(quote_currency, timestamp)
        base_usd_price = self.data_factory.get_price(base_currency, timestamp)
        quote_quantity = check_type(random.uniform(0, .1)) * quote_position.balance
        base_quantity = quote_usd_price * quote_quantity / base_usd_price
        args = {
            'base_currency': base_currency,
            'base_usd_price': base_usd_price,
            'base_quantity': base_quantity,
            'timestamp': timestamp,
            'quote_currency':  quote_currency,
            'quote_usd_price': check_type(1),
            'quote_quantity': quote_quantity,
            'mkt': 'quote'
        }
        include_fee = kwargs.get('include_fee', bool(random.randint(0, 1)))
        tx_kwargs = self.generic_factory('swap', include_fee=include_fee, **args)
        tx = Swap(**tx_kwargs)
        self.positions[base_currency].add(
            tx.id, tx.assets['base'].usd_price, tx.timestamp, tx.assets['base'].quantity)
        self.positions[quote_currency]._closes[tx.id] = {
            'timestamp': tx.timestamp,
            'price': quote_usd_price,
            'qty': quote_quantity,
            'realized_gain': 0
        }
        self.positions[quote_currency].adjust_to_mtk(quote_usd_price, timestamp)
        self.transactions.append(tx)

    def sell_factory(self, **kwargs):
        excludes = ['USD', 'USDC']
        available_assets = list([x.symbol for x in self.positions.values()
                                if x.symbol not in excludes and x.balance > 0])
        base_currency = kwargs.get("base_currency", self.get_rand_currency(available_assets, excludes=excludes))
        base_position = self.positions[base_currency]
        base_quantity = check_type(random.uniform(.1, float(base_position.balance)))
        timestamp = generate_timestamp(start=base_position.mkt_timestamp.tz_convert(tz=None))
        base_usd_price = self.data_factory.get_price(base_currency, timestamp)
        quote_quantity = base_quantity * base_usd_price
        args = {
            'base_currency': base_currency,
            'base_usd_price': base_usd_price,
            'base_quantity': base_quantity,
            'timestamp': timestamp
        }
        include_fee = kwargs.get('include_fee', bool(random.randint(0, 1)))
        tx_kwargs = self.generic_factory('sell', include_fee=include_fee, **args)
        tx_kwargs['quote_currency'] = 'USD'
        tx_kwargs['quote_usd_price'] = check_type(1)
        tx_kwargs['quote_quantity'] = quote_quantity
        tx = Sell(**tx_kwargs)
        self.positions['USD'].add(
            tx.id, check_type(1), tx.timestamp, tx.assets['quote'].quantity)
        self.positions[base_currency]._closes[tx.id] = {
            'timestamp': tx.timestamp,
            'price': base_usd_price,
            'qty': base_quantity,
            'realized_gain': 0
        }
        self.positions[base_currency].adjust_to_mtk(base_usd_price, timestamp)

        self.transactions.append(tx)

    def hardcoded_txs():
        date = datetime(year=2018, month=1, day=1)
        txs = []
        # initial 10,000 deposit. Cash 10,000, Invested Capital 10,000
        deposit_initial = Deposit(**{
            'type': 'deposit',
            'timestamp': date,
            'id': uuid.uuid4(),
            'base_currency': 'USD',
            'base_quantity': 100000,
            'base_usd_price': 1.00
        })
        txs.append(deposit_initial)
        date = datetime(year=2018, month=1, day=4)
        # initial 5 BTC buy at 1000 per btc for about 75000 USD. Cash 5000, Crypto 5000 qty 5. No fee.
        buy_btc_simple = Buy(**{
            'type': 'buy',
            'timestamp': date,
            'id': uuid.uuid4(),
            'base_currency': 'BTC',
            'base_quantity': 1,
            'base_usd_price': 15244.58,
            # 'fee_currency': 'USD',
            # 'fee_quantity': check_type(2.99),
            # 'fee_usd_price': check_type(1.00),
            'quote_currency': 'USD',
            'quote_quantity': 1 * 15244.58,
            'quote_usd_price': 1.00,
        })
        txs.append(buy_btc_simple)

        

        date = datetime(year=2018, month=1, day=8) 
               # short term gain. sell 1 btc at 2000 per coin for 1000 gain. No fee
        short_term_btc_sell_gain = Sell(**{
            'type': 'sell',
            'timestamp': date,
            'id': uuid.uuid4(),
            'base_currency': 'BTC',
            'base_quantity': .5,
            'base_usd_price': 15034,
            # 'fee_currency': 'USD',
            # 'fee_quantity': check_type(2.99),
            # 'fee_usd_price': check_type(1.00),
            'quote_currency': 'USD',
            'quote_quantity': .5 * 15034,
            'quote_usd_price': 1.00,
        })
        txs.append(short_term_btc_sell_gain)

        date = datetime(year=2018, month=1, day=12)
        # initial 5 BTC buy at 1000 per btc for about 75000 USD. Cash 5000, Crypto 5000 qty 5. No fee.
        swap_btc_eth_simple = Swap(**{
            'type': 'swap',
            'timestamp': date,
            'id': uuid.uuid4(),
            'base_currency': 'ETH',
            'base_quantity': 1,
            'base_usd_price': 1263.86,
            'fee_currency': 'BTC',
            'fee_quantity': .0001,
            'fee_usd_price': 13884.32,
            'quote_currency': 'BTC',
            'quote_quantity': .0910149,
            'quote_usd_price': 13884.32,
        })
        txs.append(swap_btc_eth_simple)



        date = date.__add__(timedelta(days=365))
        # long term gain. sell 1 btc at 4000 per coin for 3000 gain.
        long_term_btc_sell_gain = Sell(**{
            'type': 'sell',
            'timestamp': date,
            'id': uuid.uuid4(),
            'base_currency': 'BTC',
            'base_quantity': check_type(1.000000000000),
            'base_usd_price': check_type(4000.00),
            'fee_currency': 'USD',
            'fee_quantity': check_type(2.99),
            'fee_usd_price': check_type(1.00),
            'quote_currency': 'USD',
            'quote_quantity': check_type(1.000000000000) * check_type(4000.00),
            'quote_usd_price': check_type(1.00),
        })
        # txs.append(long_term_btc_sell_gain)

        date = date.__add__(timedelta(days=1))
        # long term loss. swap 1 btc at 500 per coin for 500 loss. get 10 eth for 50 per eth. no fee
        long_term_btc_swap_loss = Swap(**{
            'type': 'swap',
            'timestamp': date,
            'id': uuid.uuid4(),
            'base_currency': 'ETH',
            'base_quantity': check_type(10.000000000000),
            'base_usd_price': check_type(50.00),
            'fee_currency': 'BTC',
            'fee_quantity': check_type(.001),
            'fee_usd_price': check_type(500.00),
            'quote_currency': 'BTC',
            'quote_quantity': check_type(1.000000000000),
            'quote_usd_price': check_type(500.00),
        })
        # txs.append(long_term_btc_swap_loss)

        return txs


class HistoricalDataFactory:
    def __init__(self, start='1/1/2018', end=datetime.now(), freq='D'):
        self.date_range = pd.date_range(start=start, end=end, freq=freq, tz=pytz.UTC)
        self.data = {
            'USD': pd.DataFrame(index=self.date_range, columns=['close']),
            'BTC': pd.DataFrame(index=self.date_range, columns=['close']),
            'ETH': pd.DataFrame(index=self.date_range, columns=['close']),
            'link': pd.DataFrame(index=self.date_range, columns=['close']),
            'USDC': pd.DataFrame(index=self.date_range, columns=['close']),
            # 'grt': pd.DataFrame(index=self.date_range, columns=['close']),
            # 'ada': pd.DataFrame(index=self.date_range, columns=['close']),
        }
        for d in range(self.date_range.size):
            if d == 0:
                self.data['BTC'].iloc[d]['close'] = check_type(6000)
                self.data['ETH'].iloc[d]['close'] = check_type(150)
                # self.data['link'].iloc[d]['close'] = check_type(2)
                # self.data['grt'].iloc[d]['close'] = check_type(.05)
                # self.data['ada'].iloc[d]['close'] = check_type(.50)
            else:
                self.data['BTC'].iloc[d]['close'] = check_type(self.data['BTC'].iloc[d -
                                                                                     1]['close'] * check_type(1 + random.uniform(-2, 2.5) / 100))
                self.data['ETH'].iloc[d]['close'] = check_type(self.data['ETH'].iloc[d -
                                                                                     1]['close'] * check_type(1 + random.uniform(-3, 3.5) / 100))
                # self.data['link'].iloc[d]['close'] = check_type(self.data['link'].iloc[d -
                #                                                                        1]['close'] * check_type(1 + random.uniform(-1, 1.5) / 100))
                # self.data['grt'].iloc[d]['close'] = check_type(self.data['grt'].iloc[d -
                #                                                                      1]['close'] * check_type(1 + random.uniform(-1, 1.5) / 100))
                # self.data['ada'].iloc[d]['close'] = check_type(self.data['ada'].iloc[d -
                #                                                                      1]['close'] * check_type(1 + random.uniform(-1, 1.5) / 100))
        self.data['USD']['close'] = check_type(1)
        self.data['USDC']['close'] = check_type(1)

    def get_price(self, symbol, timestamp):
        date = datetime(year=timestamp.year,
                        month=timestamp.month, day=timestamp.day)
        return self.data[symbol].loc[date]['close']
