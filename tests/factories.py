import uuid
import random
import pandas as pd
from datetime import datetime, timedelta
from randomtimestamp import randomtimestamp
from src.crypto_accountant.utils import set_decimal
from src.crypto_accountant.position import Position
from src.crypto_accountant.transactions.buy import Buy
from src.crypto_accountant.transactions.sell import Sell
from src.crypto_accountant.transactions.swap import Swap
from src.crypto_accountant.transactions.deposit import Deposit
from src.crypto_accountant.transactions.withdrawal import Withdrawal
from src.crypto_accountant.transactions.send import Send
from src.crypto_accountant.transactions.receive import Receive


class TxnFactory:
    def __init__(self):
        self.positions = {
            'usd': Position('usd'),
            'btc': Position('btc'),
            'eth': Position('eth'),
            'link': Position('link'),
            # 'usdc': Position('usdc'),
            'grt': Position('grt'),
            'ada': Position('ada'),
        }
        self.data_factory = HistoricalDataFactory()
        self.date_range = self.data_factory.date_range
        self.eod_data = self.data_factory.data
        for symbol in self.positions.keys():
            self.positions[symbol].mkt_price = set_decimal(
                self.eod_data[symbol].iloc[0]['close'])
            self.positions[symbol].mkt_timestamp = set_decimal(
                self.eod_data[symbol].index[0])
        self.transactions = []

    def get_rand_currency(self, available_assets=[], excludes=[]):
        excludes.append('usd')
        if len(available_assets) == 0:
            available_assets = list(
                [x for x in self.positions.keys() if x not in excludes])
        return available_assets[random.randint(0, len(available_assets) - 1)]

    def generate_fee(self, qty, price=1, symbol='usd', max_pct_diff=7):
        fee = {}
        fee_total_q = qty * \
            set_decimal(random.randint(1, max_pct_diff)) * set_decimal(.01)
        fee['qty'] = fee_total_q
        fee['price'] = price
        fee['symbol'] = symbol
        return fee

    def generic_factory(self, tx_type, include_fee=False, **kwargs):
        args = {
            'type': tx_type,
            'id': kwargs.get("id", uuid.uuid4()),
            'timestamp': kwargs.get('timestamp', randomtimestamp(start_year=2018, text=False)),
            'base_currency': kwargs.get('base_currency', 'btc'),
            'base_usd_price': kwargs.get('base_usd_price', set_decimal(random.randint(8000, 10000))),
            'base_quantity': kwargs.get('base_quantity', set_decimal(random.randint(1, 10)))
        }

        if 'quote_currency' in kwargs:
            args['quote_currency'] = kwargs['quote_currency']
            args['quote_usd_price'] = kwargs['quote_usd_price']
            args['quote_quantity'] = kwargs['quote_quantity']

        if include_fee:
            mkt = kwargs.get('mkt', 'base')
            fee = self.generate_fee(args['base_quantity'], args.get(
                '{}_usd_price'.format(mkt), 1), args.get('{}_currency'.format(mkt), 'btc'))
            args['fee_quantity'] = fee['qty']
            args['fee_usd_price'] = fee['price']
            args['fee_currency'] = fee['symbol']

        print(args)
        return args

    def deposit_factory(self, base_quantity=set_decimal(random.randint(0, 10000)), include_fee=False, **kwargs):
        args = {
            'base_currency': 'usd',
            'base_usd_price': set_decimal(1),
            'base_quantity': base_quantity,
            'timestamp': kwargs.get("timestamp", randomtimestamp(start_year=2018, text=False))
        }
        tx_kwargs = self.generic_factory('deposit', include_fee=include_fee, **args)
        tx = Deposit(**tx_kwargs)
        self.positions['usd'].add(tx.id, set_decimal(
            1), tx.timestamp, tx.assets['base'].quantity)
        self.transactions.append(tx)

    def receive_factory(self, include_fee=False, **kwargs):
        base_currency = kwargs.get("base_currency", self.get_rand_currency())
        timestamp = kwargs.get("timestamp", randomtimestamp(start_year=2018, text=False))
        args = {
            'base_currency': base_currency,
            'base_usd_price': self.data_factory.get_price(base_currency, timestamp),
            'base_quantity': kwargs.get('base_quantity', set_decimal(random.randint(1, 100))),
            'timestamp': timestamp
        }
        tx_kwargs = self.generic_factory('receive', include_fee=include_fee, **args)
        tx = Receive(**tx_kwargs)
        self.positions[base_currency].add(
            tx.id, tx.assets['base'].usd_price, tx.timestamp, tx.assets['base'].quantity)
        self.transactions.append(tx)

    def buy_factory(self, **kwargs):
        base_currency = kwargs.get("base_currency", self.get_rand_currency())
        timestamp = randomtimestamp(
            start=self.positions['usd'].mkt_timestamp, text=False)
        quote_quantity = set_decimal(
            random.uniform(.1, float(self.positions['usd'].balance)))
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
        tx_kwargs['quote_currency'] =  'usd'
        tx_kwargs['quote_usd_price'] = set_decimal(1)
        tx_kwargs['quote_quantity'] = quote_quantity
        tx = Buy(**tx_kwargs)
        self.positions[base_currency].add(
            tx.id, tx.assets['base'].usd_price, tx.timestamp, tx.assets['base'].quantity)
        self.positions['usd']._closes[tx.id] = {
            'timestamp': tx.timestamp,
            'price': set_decimal(1),
            'qty': quote_quantity,
            'realized_gain': 0
        }
        self.positions['usd'].adjust_to_mtk(set_decimal(1), timestamp)
        self.transactions.append(tx)

    def swap_factory(self, **kwargs):
        available_assets = list([x.symbol for x in self.positions.values() if x.balance > 0])
        print(available_assets)
        base_currency = kwargs.get("base_currency", self.get_rand_currency())
        quote_currency = kwargs.get("base_currency", self.get_rand_currency(available_assets, excludes=[base_currency]))
        quote_position = self.positions[quote_currency]
        timestamp = kwargs.get("timestamp", randomtimestamp(
            start=quote_position.mkt_timestamp, text=False))
        quote_usd_price = self.data_factory.get_price(quote_currency, timestamp)
        base_usd_price = self.data_factory.get_price(base_currency, timestamp)
        quote_quantity = set_decimal(random.uniform(0, .1)) * quote_position.balance
        base_quantity = quote_usd_price * quote_quantity / base_usd_price
        args = {
            'base_currency': base_currency,
            'base_usd_price': base_usd_price,
            'base_quantity': base_quantity,
            'timestamp': timestamp,
            'quote_currency':  quote_currency,
            'quote_usd_price': set_decimal(1),
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
        excludes=['usd', 'usdc']
        available_assets = list([x.symbol for x in self.positions.values() if x.symbol not in excludes and x.balance > 0])
        print("AVAILABLE SELL", available_assets)
        base_currency = kwargs.get("base_currency", self.get_rand_currency(available_assets, excludes=excludes))
        print("BASE SELL", base_currency)
        base_position = self.positions[base_currency]
        base_quantity = set_decimal(random.uniform(.1, float(base_position.balance)))
        timestamp = randomtimestamp(start=base_position.mkt_timestamp, text=False)
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
        tx_kwargs['quote_currency'] =  'usd'
        tx_kwargs['quote_usd_price'] = set_decimal(1)
        tx_kwargs['quote_quantity'] = quote_quantity
        tx = Sell(**tx_kwargs)
        self.positions['usd'].add(
            tx.id, set_decimal(1), tx.timestamp, tx.assets['quote'].quantity)
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
            'base_currency': 'usd',
            'base_quantity': set_decimal(10000.00),
            'base_usd_price': set_decimal(1.00)
            })
        txs.append(deposit_initial)
        date = date.__add__(timedelta(days=2))
        # initial 5 BTC buy at 1000 per btc for 5000 USD. Cash 5000, Crypto 5000 qty 5. No fee.
        buy_btc_simple = Buy(**{
            'type': 'buy',
            'timestamp': date,
            'id': uuid.uuid4(),
            'base_currency': 'btc',
            'base_quantity': set_decimal(5.000000000000),
            'base_usd_price': set_decimal(1000.00),
            # 'fee_currency': 'usd',
            # 'fee_quantity': set_decimal(2.99),
            # 'fee_usd_price': set_decimal(1.00),
            'quote_currency': 'usd',
            'quote_quantity': set_decimal(5.000000000000) * set_decimal(1000.00),
            'quote_usd_price': set_decimal(1.00),
            })
        txs.append(buy_btc_simple)    

        date = date.__add__(timedelta(days=180))            
        # short term gain. sell 1 btc at 2000 per coin for 1000 gain. No fee
        short_term_btc_sell_gain = Sell(**{
            'type': 'sell',
            'timestamp': date,
            'id': uuid.uuid4(),
            'base_currency': 'btc',
            'base_quantity': set_decimal(1.000000000000),
            'base_usd_price': set_decimal(2000.00),
            # 'fee_currency': 'usd',
            # 'fee_quantity': set_decimal(2.99),
            # 'fee_usd_price': set_decimal(1.00),
            'quote_currency': 'usd',
            'quote_quantity': set_decimal(1.000000000000) * set_decimal(2000.00),
            'quote_usd_price': set_decimal(1.00),
            })
        txs.append(short_term_btc_sell_gain)    

        date = date.__add__(timedelta(days=365))            
        # long term gain. sell 1 btc at 4000 per coin for 3000 gain. 
        long_term_btc_sell_gain = Sell(**{
            'type': 'sell',
            'timestamp': date,
            'id': uuid.uuid4(),
            'base_currency': 'btc',
            'base_quantity': set_decimal(1.000000000000),
            'base_usd_price': set_decimal(4000.00),
            'fee_currency': 'usd',
            'fee_quantity': set_decimal(2.99),
            'fee_usd_price': set_decimal(1.00),
            'quote_currency': 'usd',
            'quote_quantity': set_decimal(1.000000000000) * set_decimal(4000.00),
            'quote_usd_price': set_decimal(1.00),
            })
        txs.append(long_term_btc_sell_gain)    

        date = date.__add__(timedelta(days=1))            
        # long term loss. swap 1 btc at 500 per coin for 500 loss. get 10 eth for 50 per eth. no fee 
        long_term_btc_swap_loss = Swap(**{
            'type': 'swap',
            'timestamp': date,
            'id': uuid.uuid4(),
            'base_currency': 'eth',
            'base_quantity': set_decimal(10.000000000000),
            'base_usd_price': set_decimal(50.00),
            'fee_currency': 'btc',
            'fee_quantity': set_decimal(.001),
            'fee_usd_price': set_decimal(500.00),
            'quote_currency': 'btc',
            'quote_quantity': set_decimal(1.000000000000),
            'quote_usd_price': set_decimal(500.00),
            })
        txs.append(long_term_btc_swap_loss)
              
        return txs


class HistoricalDataFactory:
    def __init__(self, start='1/1/2018', end=datetime.now(), freq='D'):
        self.date_range = pd.date_range(start=start, end=end, freq=freq)
        self.data = {
            'usd': pd.DataFrame(index=self.date_range, columns=['close']),
            'btc': pd.DataFrame(index=self.date_range, columns=['close']),
            'eth': pd.DataFrame(index=self.date_range, columns=['close']),
            'link': pd.DataFrame(index=self.date_range, columns=['close']),
            'usdc': pd.DataFrame(index=self.date_range, columns=['close']),
            'grt': pd.DataFrame(index=self.date_range, columns=['close']),
            'ada': pd.DataFrame(index=self.date_range, columns=['close']),
        }
        for d in range(self.date_range.size):
            if d == 0:
                self.data['btc'].iloc[d]['close'] = set_decimal(6000)
                self.data['eth'].iloc[d]['close'] = set_decimal(150)
                self.data['link'].iloc[d]['close'] = set_decimal(2)
                self.data['grt'].iloc[d]['close'] = set_decimal(.05)
                self.data['ada'].iloc[d]['close'] = set_decimal(.50)
            else:
                self.data['btc'].iloc[d]['close'] = set_decimal(self.data['btc'].iloc[d -
                                                                                      1]['close'] * set_decimal(1 + random.uniform(-2, 2.5) / 100))
                self.data['eth'].iloc[d]['close'] = set_decimal(self.data['eth'].iloc[d -
                                                                                      1]['close'] * set_decimal(1 + random.uniform(-3, 3.5) / 100))
                self.data['link'].iloc[d]['close'] = set_decimal(self.data['link'].iloc[d -
                                                                                        1]['close'] * set_decimal(1 + random.uniform(-1, 1.5) / 100))
                self.data['grt'].iloc[d]['close'] = set_decimal(self.data['grt'].iloc[d -
                                                                                      1]['close'] * set_decimal(1 + random.uniform(-1, 1.5) / 100))
                self.data['ada'].iloc[d]['close'] = set_decimal(self.data['ada'].iloc[d -
                                                                                      1]['close'] * set_decimal(1 + random.uniform(-1, 1.5) / 100))
        self.data['usd']['close'] = set_decimal(1)
        self.data['usdc']['close'] = set_decimal(1)

    def get_price(self, symbol, timestamp):
        date = datetime(year=timestamp.year,
                        month=timestamp.month, day=timestamp.day)
        return self.data[symbol].loc[date]['close']
